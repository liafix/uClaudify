package com.finbridge.legacy;

import java.util.List;

public final class CanonicalContract {
    private CanonicalContract() {}

    public static final List<String> TRANSACTION_FIELDS = List.of(
        "transaction_id",
        "account_id",
        "booking_date",
        "amount",
        "currency",
        "direction",
        "counterparty",
        "source_system"
    );

    public static final String SOURCE_SYSTEM = "AlpineBank Legacy Finance";
    public static final String BATCH_ID = "2026-09-05-001";
}
