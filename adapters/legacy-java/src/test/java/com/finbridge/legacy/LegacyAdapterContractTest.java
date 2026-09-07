package com.finbridge.legacy;

import java.util.List;

public final class LegacyAdapterContractTest {
    private LegacyAdapterContractTest() {}

    public static void main(String[] args) {
        List<String> expected = List.of(
            "transaction_id",
            "account_id",
            "booking_date",
            "amount",
            "currency",
            "direction",
            "counterparty",
            "source_system"
        );

        if (!CanonicalContract.TRANSACTION_FIELDS.equals(expected)) {
            throw new AssertionError("Canonical transaction field contract changed");
        }
        if (!CanonicalContract.BATCH_ID.equals("2026-09-05-001")) {
            throw new AssertionError("Frozen batch id changed");
        }
        if (!CanonicalContract.SOURCE_SYSTEM.equals("AlpineBank Legacy Finance")) {
            throw new AssertionError("Frozen source system changed");
        }

        System.out.println("Legacy Java PASS 0 contract: PASS");
    }
}
