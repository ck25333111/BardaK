#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ Проект:    HH Test Task - Email Checker                                      ║
║ Файл:      email_check.py                                                    ║
║ Назначение:                                                                 ║
║   Проверка email-адресов по домену:                                          ║
║     1) существует ли домен (NXDOMAIN -> "домен отсутствует")                 ║
║     2) есть ли корректные MX-записи ("MX-записи отсутствуют или некорректны")║
║     3) (опционально) SMTP handshake до RCPT TO (не 100% надежно)             ║
║                                                                              ║
║ Установка:                                                                   ║
║   pip install dnspython                                                      ║
║                                                                              ║
║ Запуск:                                                                      ║
║   python email_check.py --input emails.txt                                   ║
║   python email_check.py --input emails.txt --smtp --details                  ║
║                                                                              ║
║ Примечания про SMTP:                                                         ║
║   SMTP-проверка существования конкретного ящика НЕ гарантирована.            ║
║   Сервер может:                                                               ║
║     - принимать любого получателя (catch-all)                                 ║
║     - резать по антиспаму / greylist                                         ║
║     - требовать STARTTLS/политики                                             ║
║   Поэтому основной статус задачи — домен/MX. SMTP — лишь доп.деталь.         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import argparse
import asyncio
import re
import socket
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence, Tuple

import dns.exception  # type: ignore
import dns.resolver  # type: ignore


# =============================================================================
# МОДЕЛИ/СТРУКТУРЫ ДАННЫХ
# =============================================================================

class DomainStatus(str, Enum):
    """
    Основные статусы, которые требует тестовое задание.

    Мы возвращаем РОВНО эти формулировки:
    - "домен валиден" — домен существует и MX-записи выглядят рабочими
    - "домен отсутствует" — домен не существует (NXDOMAIN)
    - "MX-записи отсутствуют или некорректны" — нет MX, или MX "битые"
    """
    DOMAIN_VALID = "домен валиден"
    DOMAIN_MISSING = "домен отсутствует"
    MX_BAD = "MX-записи отсутствуют или некорректны"


class SmtpVerdict(str, Enum):
    """
    Дополнительный результат SMTP-проверки (не основной статус из задания).

    Нужен, чтобы в режиме --details понимать, что конкретно произошло на SMTP:
    - OK: сервер принял RCPT TO (не значит 100% что ящик реально есть)
    - USER_REJECTED: сервер сказал "нет такого получателя" (5xx/550)
    - TEMPORARY: временный отказ (4xx)
    - BLOCKED_OR_FILTERED: явно режут/фильтруют (например 421 или MAIL FROM reject)
    - CONNECT_FAILED: не смогли подключиться/таймаут
    - PROTOCOL_ERROR: сервер отвечает криво/сбой диалога
    - UNKNOWN: что-то странное по кодам
    """
    NOT_REQUESTED = "not_requested"
    OK = "ok"
    USER_REJECTED = "user_rejected"
    TEMPORARY = "temporary"
    BLOCKED_OR_FILTERED = "blocked_or_filtered"
    CONNECT_FAILED = "connect_failed"
    PROTOCOL_ERROR = "protocol_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class EmailInput:
    """
    Результат минимального парсинга email.

    Поля:
    - raw: исходная строка
    - local: часть до @
    - domain: часть после @ (lowercase, без завершающей точки)
    """
    raw: str
    local: str
    domain: str

    @staticmethod
    def parse(value: str) -> Optional["EmailInput"]:
        """
        Минимально разбирает строку email в формат local@domain.

        Что делает:
        - тримит пробелы
        - делит по последнему символу "@"
        - домен приводит к lowercase и убирает завершающую точку
        - проверяет, что домен содержит только [a-z0-9.-] (упрощение)

        Возвращает:
        - EmailInput, если формат более-менее похож на email
        - None, если строка совсем мусор

        Важно:
        - Это НЕ полноценная RFC-валидация email (она огромная и не нужна для задачи).
        - IDN/кириллица в домене тут не поддержаны — для тестового обычно ок.
        """
        v = value.strip()
        if not v or "@" not in v:
            return None

        local, domain = v.rsplit("@", 1)
        local = local.strip()
        domain = domain.strip().strip(".").lower()

        if not local or not domain:
            return None

        if not re.fullmatch(r"[a-z0-9.-]+", domain):
            return None

        return EmailInput(raw=v, local=local, domain=domain)


@dataclass(frozen=True)
class MxRecord:
    """
    Одна MX-запись домена.

    Поля:
    - host: имя MX-сервера (например mx1.example.com)
    - priority: приоритет (меньше = важнее)
    """
    host: str
    priority: int


@dataclass(frozen=True)
class EmailCheckResult:
    """
    Итог проверки одного email.

    Поля:
    - email: исходный email
    - status: основной статус по требованиям задания (DomainStatus)
    - domain: извлечённый домен
    - mx: список MX (если нашли)
    - smtp_verdict: доп.результат SMTP (если включен флаг --smtp)
    - smtp_code/smtp_message: код/сообщение SMTP-ответа, если есть
    - error: текст ошибки/пояснение (для --details полезно)
    """
    email: str
    status: DomainStatus
    domain: str
    mx: Tuple[MxRecord, ...] = ()
    smtp_verdict: SmtpVerdict = SmtpVerdict.NOT_REQUESTED
    smtp_code: Optional[int] = None
    smtp_message: Optional[str] = None
    error: Optional[str] = None


# =============================================================================
# КОНФИГ
# =============================================================================

@dataclass(frozen=True)
class EmailCheckConfig:
    """
    Конфигурация проверки.

    Поля:
    - concurrency_limit: сколько email одновременно проверяем (ограничение параллелизма)
    - dns_timeout_sec: таймаут DNS запросов
    - smtp_timeout_sec: таймаут на SMTP операции
    - smtp_port: порт SMTP (обычно 25 для входящей почты)
    - smtp_try_mx_hosts: сколько MX-хостов пробовать по очереди
    - smtp_sender: какой MAIL FROM использовать в handshake
    - enable_smtp: включить ли SMTP проверку RCPT TO
    """
    concurrency_limit: int = 50
    dns_timeout_sec: float = 4.0
    smtp_timeout_sec: float = 8.0
    smtp_port: int = 25
    smtp_try_mx_hosts: int = 2
    smtp_sender: str = "check@localhost"
    enable_smtp: bool = False


# =============================================================================
# ОШИБКИ (чтобы различать NXDOMAIN и временные проблемы)
# =============================================================================

class DomainMissingError(Exception):
    """Исключение: домен не существует (NXDOMAIN)."""


class DnsTransientError(Exception):
    """Исключение: временная DNS проблема (timeout, no nameservers, и т.д.)."""


# =============================================================================
# DNS-КЛИЕНТ (MX lookup)
# =============================================================================

class DnsClient:
    """
    Обёртка над dnspython для получения MX-записей.

    Зачем отдельный класс:
    - логика маппинга исключений в "домен отсутствует" vs "MX плохие" держится тут
    - тестировать/заменять проще
    """

    def __init__(self, timeout_sec: float) -> None:
        """
        Создаёт DNS-резолвер и ставит таймауты.

        timeout_sec влияет на:
        - timeout: ожидание ответа одного сервера
        - lifetime: суммарное время резолва
        """
        self._resolver = dns.resolver.Resolver()
        self._resolver.lifetime = timeout_sec
        self._resolver.timeout = timeout_sec

    def get_mx(self, domain: str) -> Tuple[MxRecord, ...]:
        """
        Возвращает MX-записи для домена, отсортированные по приоритету.

        Варианты исхода:
        - Возвращает () если MX нет (NoAnswer)
        - Поднимает DomainMissingError если домен не существует (NXDOMAIN)
        - Поднимает DnsTransientError если DNS временно сломан/не отвечает

        Почему так:
        - По задаче нужен отдельный статус "домен отсутствует"
        - Все остальные DNS-неприятности проще относить к MX_BAD (по заданию нет статуса "не удалось проверить")
        """
        try:
            answers = self._resolver.resolve(domain, "MX")
        except dns.resolver.NXDOMAIN as e:
            raise DomainMissingError(str(e)) from e
        except dns.resolver.NoAnswer:
            return ()
        except dns.resolver.NoNameservers as e:
            raise DnsTransientError(str(e)) from e
        except dns.exception.Timeout as e:
            raise DnsTransientError("DNS timeout") from e
        except Exception as e:
            raise DnsTransientError(f"DNS error: {e}") from e

        mx: List[MxRecord] = []
        for r in answers:
            # dnspython отдаёт: preference + exchange
            host = str(r.exchange).rstrip(".").lower()
            prio = int(r.preference)
            mx.append(MxRecord(host=host, priority=prio))

        mx.sort(key=lambda x: x.priority)
        return tuple(mx)


# =============================================================================
# SMTP-КЛИЕНТ (handshake до RCPT TO)
# =============================================================================

class SmtpClient:
    """
    Минимальный SMTP-клиент, который НЕ отправляет письмо.

    Мы делаем только:
    - connect
    - читаем banner
    - EHLO (или HELO fallback)
    - MAIL FROM
    - RCPT TO
    - QUIT

    Это позволяет "попробовать" узнать, примет ли сервер конкретного получателя.

    Важно:
    - Реальный мир грязный: антиспам, greylisting, catch-all.
    - Поэтому результат SMTP — доп.информация, а не основная истина.
    """

    def __init__(self, timeout_sec: float, port: int) -> None:
        """
        Сохраняет таймауты и порт.

        timeout_sec используется для:
        - подключения
        - чтения строк ответа
        - drain (отправки команд)
        """
        self._timeout = timeout_sec
        self._port = port

    async def check_rcpt(self, host: str, sender: str, rcpt: str) -> Tuple[SmtpVerdict, Optional[int], str]:
        """
        Пытается выполнить SMTP диалог с host и проверить RCPT TO.

        Параметры:
        - host: MX-хост (например mx.yandex.ru)
        - sender: что ставим в MAIL FROM
        - rcpt: проверяемый получатель (email)

        Возвращает:
        (verdict, code, message)
        - verdict: SmtpVerdict (OK/USER_REJECTED/и т.д.)
        - code: SMTP код (если удалось прочитать), иначе None
        - message: строка/строки ответа (для дебага)

        Почему возвращаем message:
        - ты можешь увидеть в --details, чем конкретно сервер недоволен.
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, self._port),
                timeout=self._timeout,
            )
        except Exception as e:
            return (SmtpVerdict.CONNECT_FAILED, None, f"connect failed: {e}")

        async def _read_resp() -> Tuple[int, str]:
            """
            Читает SMTP ответ, учитывая многострочные ответы.

            SMTP может отвечать так:
              250-строка1
              250-строка2
              250 строка_последняя

            Правило:
            - если 4-й символ '-' → ещё строки будут
            - если 4-й символ ' ' → последняя строка ответа
            """
            lines: List[str] = []
            code: Optional[int] = None

            while True:
                raw = await asyncio.wait_for(reader.readline(), timeout=self._timeout)
                if not raw:
                    raise RuntimeError("empty response")

                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                lines.append(line)

                if len(line) >= 3 and line[:3].isdigit():
                    code = int(line[:3])

                # Многострочный ответ: "250-...."
                if len(line) >= 4 and line[3] == "-":
                    continue
                break

            if code is None:
                raise RuntimeError("no status code")
            return code, "\n".join(lines)

        async def _send(cmd: str) -> None:
            """
            Отправляет SMTP команду (добавляет CRLF) и ждёт, пока она уйдет в сеть.
            """
            writer.write((cmd + "\r\n").encode("utf-8"))
            await asyncio.wait_for(writer.drain(), timeout=self._timeout)

        try:
            # 1) banner
            await _read_resp()

            # 2) EHLO (и HELO fallback)
            await _send("EHLO localhost")
            code, msg = await _read_resp()
            if code >= 500:
                await _send("HELO localhost")
                code, msg = await _read_resp()
                if code >= 500:
                    return (SmtpVerdict.PROTOCOL_ERROR, code, f"EHLO/HELO rejected: {msg}")

            # 3) MAIL FROM
            await _send(f"MAIL FROM:<{sender}>")
            code, msg = await _read_resp()
            if code >= 500:
                # часто антиспам: режут на MAIL FROM или по IP
                return (SmtpVerdict.BLOCKED_OR_FILTERED, code, f"MAIL FROM rejected: {msg}")

            # 4) RCPT TO — вот тут главное
            await _send(f"RCPT TO:<{rcpt}>")
            code, msg = await _read_resp()

            return (self._map_rcpt_code(code), code, msg)

        except asyncio.TimeoutError:
            return (SmtpVerdict.CONNECT_FAILED, None, "timeout")
        except Exception as e:
            return (SmtpVerdict.PROTOCOL_ERROR, None, f"protocol error: {e}")
        finally:
            # Всегда пытаемся закрыть соединение корректно.
            try:
                writer.write(b"QUIT\r\n")
                await writer.drain()
            except Exception:
                pass
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    @staticmethod
    def _map_rcpt_code(code: int) -> SmtpVerdict:
        """
        Превращает SMTP код ответа на RCPT TO в человеко-понятный verdict.

        Упрощенная логика:
        - 2xx: принято (OK)
        - 4xx: временно (TEMPORARY)
        - 5xx/550: отказ (USER_REJECTED)
        - 421: часто блок/закрытие соединения
        - остальное: UNKNOWN
        """
        if 200 <= code < 300:
            return SmtpVerdict.OK
        if code in {450, 451, 452}:
            return SmtpVerdict.TEMPORARY
        if code == 421:
            return SmtpVerdict.BLOCKED_OR_FILTERED
        if code == 550 or (500 <= code < 600):
            return SmtpVerdict.USER_REJECTED
        return SmtpVerdict.UNKNOWN


# =============================================================================
# СЕРВИС ПРОВЕРКИ EMAIL (асинхронно + ограничение параллельности)
# =============================================================================

class EmailChecker:
    """
    Главный сервис.

    Он делает:
    - читает email
    - парсит домен
    - запрашивает MX
    - проверяет "валидность" MX
    - (опционально) делает SMTP handshake

    Асинхронность:
    - Мы запускаем много проверок одновременно, но ограничиваем семафором,
      чтобы не убить сеть и не получить баны.
    """

    def __init__(self, dns_client: DnsClient, smtp_client: SmtpClient, cfg: EmailCheckConfig) -> None:
        """
        Инициализация:
        - сохраняем клиентов DNS/SMTP
        - сохраняем конфиг
        - создаем semaphore по concurrency_limit
        """
        self._dns = dns_client
        self._smtp = smtp_client
        self._cfg = cfg
        self._sem = asyncio.Semaphore(cfg.concurrency_limit)

    async def check_many(self, emails: Sequence[str]) -> List[EmailCheckResult]:
        """
        Проверяет список email параллельно.

        Создаёт задачи asyncio для каждого email и ждёт результат.
        concurrency_limit работает внутри _guarded_check_one.
        """
        tasks = [asyncio.create_task(self._guarded_check_one(e)) for e in emails]
        return await asyncio.gather(*tasks)

    async def _guarded_check_one(self, raw_email: str) -> EmailCheckResult:
        """
        Оборачивает проверку одного email семафором.

        Это нужно, чтобы ограничить количество одновременных сетевых операций.
        """
        async with self._sem:
            return await self.check_one(raw_email)

    async def check_one(self, raw_email: str) -> EmailCheckResult:
        """
        Проверяет один email и возвращает EmailCheckResult.

        Логика:
        1) parse email -> домен
        2) запрос MX:
           - NXDOMAIN -> DOMAIN_MISSING
           - нет MX -> MX_BAD
           - временный DNS фейл -> MX_BAD (по заданию нет статуса "не удалось проверить")
        3) проверка что MX не "null MX"
        4) проверка что MX-хост резолвится в IP (A/AAAA) — защита от "битых" MX
        5) если включен --smtp: handshake до RCPT TO
        """
        parsed = EmailInput.parse(raw_email)
        if parsed is None:
            # В задании нет статуса "невалидный email", поэтому:
            # считаем это как "домен отсутствует" + пояснение в error.
            return EmailCheckResult(
                email=raw_email.strip(),
                status=DomainStatus.DOMAIN_MISSING,
                domain="",
                error="invalid email format",
            )

        # MX lookup
        try:
            mx = self._dns.get_mx(parsed.domain)
        except DomainMissingError as e:
            return EmailCheckResult(
                email=parsed.raw,
                status=DomainStatus.DOMAIN_MISSING,
                domain=parsed.domain,
                error=str(e),
            )
        except DnsTransientError as e:
            return EmailCheckResult(
                email=parsed.raw,
                status=DomainStatus.MX_BAD,
                domain=parsed.domain,
                error=str(e),
            )

        if not mx:
            return EmailCheckResult(
                email=parsed.raw,
                status=DomainStatus.MX_BAD,
                domain=parsed.domain,
                mx=(),
            )

        # Null MX: иногда домен явно заявляет "почту не принимаю"
        if any(r.host in {".", ""} for r in mx):
            return EmailCheckResult(
                email=parsed.raw,
                status=DomainStatus.MX_BAD,
                domain=parsed.domain,
                mx=mx,
                error="null MX (domain does not accept email)",
            )

        # Проверка, что MX хосты реально резолвятся
        good_mx: List[MxRecord] = []
        for r in mx:
            if await self._mx_host_resolves(r.host):
                good_mx.append(r)

        if not good_mx:
            return EmailCheckResult(
                email=parsed.raw,
                status=DomainStatus.MX_BAD,
                domain=parsed.domain,
                mx=mx,
                error="MX hosts do not resolve",
            )

        # Основной статус по заданию: домен валиден
        status = DomainStatus.DOMAIN_VALID

        # SMTP — опционально
        if not self._cfg.enable_smtp:
            return EmailCheckResult(
                email=parsed.raw,
                status=status,
                domain=parsed.domain,
                mx=tuple(good_mx),
                smtp_verdict=SmtpVerdict.NOT_REQUESTED,
            )

        verdict, code, msg = await self._smtp_try_hosts(tuple(good_mx), parsed.raw)
        return EmailCheckResult(
            email=parsed.raw,
            status=status,
            domain=parsed.domain,
            mx=tuple(good_mx),
            smtp_verdict=verdict,
            smtp_code=code,
            smtp_message=msg,
        )

    async def _mx_host_resolves(self, host: str) -> bool:
        """
        Проверяет, что MX-хост резолвится в IP адрес (A/AAAA).

        Почему это async:
        - socket.getaddrinfo — блокирующий вызов.
        - Мы отправляем его в отдельный thread через asyncio.to_thread(),
          чтобы не блокировать event loop.
        """
        def _resolve() -> bool:
            try:
                socket.getaddrinfo(host, None)
                return True
            except socket.gaierror:
                return False

        return await asyncio.to_thread(_resolve)

    async def _smtp_try_hosts(self, mx: Tuple[MxRecord, ...], rcpt: str) -> Tuple[SmtpVerdict, Optional[int], str]:
        """
        Пробует SMTP-проверку на нескольких MX-хостах по очереди.

        Зачем:
        - у домена может быть несколько MX,
        - один может быть недоступен,
        - другой может ответить.

        Останавливаемся раньше, если получили "осмысленный" результат:
        - OK или USER_REJECTED (сервер принял или отказал получателя).
        """
        tries = 0
        last: Tuple[SmtpVerdict, Optional[int], str] = (SmtpVerdict.CONNECT_FAILED, None, "no tries")

        for r in mx:
            tries += 1
            last = await self._smtp.check_rcpt(
                host=r.host,
                sender=self._cfg.smtp_sender,
                rcpt=rcpt,
            )
            verdict = last[0]

            if verdict in {SmtpVerdict.OK, SmtpVerdict.USER_REJECTED}:
                return last

            if tries >= self._cfg.smtp_try_mx_hosts:
                break

        return last


# =============================================================================
# CLI (чтение файла, вывод результата, параметры)
# =============================================================================

def read_emails(path: str) -> List[str]:
    """
    Читает emails из файла.

    Формат:
    - один email в строке
    - пустые строки игнорируются
    """
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def format_result(r: EmailCheckResult, details: bool) -> str:
    """
    Форматирует результат проверки в строку для печати.

    Если details=False:
    - печатает только: "<email> => <статус>"

    Если details=True:
    - добавляет domain, mx, smtp verdict, smtp code/message, error
    """
    base = f"{r.email}\t=> {r.status.value}"
    if not details:
        return base

    parts = [base, f"domain={r.domain or '-'}"]
    parts.append("mx=" + (",".join(f"{m.priority}:{m.host}" for m in r.mx) if r.mx else "-"))

    if r.smtp_verdict != SmtpVerdict.NOT_REQUESTED:
        parts.append(f"smtp={r.smtp_verdict.value}")
        if r.smtp_code is not None:
            parts.append(f"code={r.smtp_code}")
        if r.smtp_message:
            parts.append("msg=" + r.smtp_message.replace("\n", " | ")[:200])

    if r.error:
        parts.append(f"err={r.error}")

    return " | ".join(parts)


def build_parser() -> argparse.ArgumentParser:
    """
    Собирает argparse-парсер.

    Параметры:
    --input        файл с email (обязательно)
    --smtp         включить SMTP handshake до RCPT TO
    --details      печатать расширенные детали
    --limit        ограничение параллельности
    --dns-timeout  таймаут DNS
    --smtp-timeout таймаут SMTP
    --smtp-port    SMTP порт (обычно 25)
    --smtp-try-mx  сколько MX хостов пробовать в SMTP
    --smtp-sender  значение для MAIL FROM
    """
    p = argparse.ArgumentParser(description="Email domain/MX checker + optional SMTP handshake.")
    p.add_argument("--input", required=True, help="Файл с email (по одному в строке).")
    p.add_argument("--smtp", action="store_true", help="Включить SMTP RCPT check (может быть ненадежно).")
    p.add_argument("--details", action="store_true", help="Печатать детали (MX, коды SMTP, ошибки).")
    p.add_argument("--limit", type=int, default=50, help="Лимит параллельности. По умолчанию: 50")
    p.add_argument("--dns-timeout", type=float, default=4.0, help="Таймаут DNS в секундах. По умолчанию: 4.0")
    p.add_argument("--smtp-timeout", type=float, default=8.0, help="Таймаут SMTP в секундах. По умолчанию: 8.0")
    p.add_argument("--smtp-port", type=int, default=25, help="SMTP порт. По умолчанию: 25")
    p.add_argument("--smtp-try-mx", type=int, default=2, help="Сколько MX хостов пробовать. По умолчанию: 2")
    p.add_argument("--smtp-sender", default="check@localhost", help="MAIL FROM sender. По умолчанию: check@localhost")
    return p


async def run(args: argparse.Namespace) -> int:
    """
    Точка запуска логики проверки.

    Делает:
    1) читает email из файла
    2) собирает конфиг
    3) создаёт клиентов DNS/SMTP и EmailChecker
    4) печатает результаты
    5) возвращает exit code (0 — успех, 1/2 — ошибки)
    """
    emails = read_emails(args.input)
    if not emails:
        print("Пустой список email.", file=sys.stderr)
        return 1

    cfg = EmailCheckConfig(
        concurrency_limit=args.limit,
        dns_timeout_sec=args.dns_timeout,
        smtp_timeout_sec=args.smtp_timeout,
        smtp_port=args.smtp_port,
        smtp_try_mx_hosts=args.smtp_try_mx,
        smtp_sender=args.smtp_sender,
        enable_smtp=args.smtp,
    )

    checker = EmailChecker(
        dns_client=DnsClient(timeout_sec=cfg.dns_timeout_sec),
        smtp_client=SmtpClient(timeout_sec=cfg.smtp_timeout_sec, port=cfg.smtp_port),
        cfg=cfg,
    )

    results = await checker.check_many(emails)
    for r in results:
        print(format_result(r, details=args.details))

    return 0


def main() -> None:
    """
    Главная функция CLI.

    Парсит аргументы и запускает async run() через asyncio.run().
    """
    args = build_parser().parse_args()
    raise SystemExit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()