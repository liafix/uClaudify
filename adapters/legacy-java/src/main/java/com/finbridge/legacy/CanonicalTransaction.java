package com.finbridge.legacy;

import java.math.BigDecimal;

/** Transport-only representation of the frozen FinBridge canonical CSV contract. */
public record CanonicalTransaction(
    String transactionId,
    String accountId,
    String bookingDate,
    BigDecimal amount,
    String currency,
    String direction,
    String counterparty,
    String sourceSystem
) {}
