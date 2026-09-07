package com.finbridge.legacy;

/** Structural adapter only. It does not own data-quality or finance decisions. */
public final class LegacyTransactionMapper {
    private LegacyTransactionMapper() {}

    public static CanonicalTransaction toCanonical(LegacyTransaction source) {
        String direction = switch (source.movementCode()) {
            case "CR" -> "CREDIT";
            case "DR" -> "DEBIT";
            default -> throw new IllegalArgumentException("Unsupported legacy movement code: " + source.movementCode());
        };
        return new CanonicalTransaction(
            source.transactionRef(),
            source.ledgerAccount(),
            source.bookingDate(),
            source.amount(),
            source.currencyCode(),
            direction,
            source.counterpartyName(),
            CanonicalContract.SOURCE_SYSTEM
        );
    }
}
