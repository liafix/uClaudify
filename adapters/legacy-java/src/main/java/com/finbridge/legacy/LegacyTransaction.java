package com.finbridge.legacy;

import java.math.BigDecimal;

/** Fictional AlpineBank legacy-source transaction shape. */
public record LegacyTransaction(
    String transactionRef,
    String ledgerAccount,
    String bookingDate,
    BigDecimal amount,
    String currencyCode,
    String movementCode,
    String counterpartyName
) {}
