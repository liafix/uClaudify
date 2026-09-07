package com.finbridge.legacy;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public final class LegacyAdapterPass4Test {
    private LegacyAdapterPass4Test() {}

    public static void main(String[] args) throws Exception {
        List<LegacyTransaction> source = LegacySyntheticSource.buildBatch();
        if (source.size() != 1024) {
            throw new AssertionError("Expected exactly 1,024 legacy rows");
        }

        long duplicateCount = source.stream()
            .filter(row -> List.of("TX-00482", "TX-00791", "TX-00902").contains(row.transactionRef()))
            .count();
        if (duplicateCount != 6) {
            throw new AssertionError("Original + repeated frozen duplicate ids must both cross the Java boundary");
        }
        if (source.stream().noneMatch(row -> row.currencyCode().equals("EUX"))
            || source.stream().noneMatch(row -> row.currencyCode().equals("EURO"))) {
            throw new AssertionError("Invalid currencies were incorrectly repaired by Java");
        }

        CanonicalTransaction credit = LegacyTransactionMapper.toCanonical(source.get(0));
        if (!credit.direction().equals("CREDIT")) {
            throw new AssertionError("CR movement code must map structurally to CREDIT");
        }
        CanonicalTransaction debit = source.stream()
            .filter(row -> row.movementCode().equals("DR"))
            .findFirst()
            .map(LegacyTransactionMapper::toCanonical)
            .orElseThrow();
        if (!debit.direction().equals("DEBIT")) {
            throw new AssertionError("DR movement code must map structurally to DEBIT");
        }

        Path tmp = Files.createTempFile("finbridge-java-canonical-", ".csv");
        try {
            LegacyAdapterApp.main(new String[] {tmp.toString()});
            List<String> lines = Files.readAllLines(tmp);
            if (lines.size() != 1025) {
                throw new AssertionError("Canonical CSV must contain one header + 1,024 records");
            }
            if (!lines.get(0).equals(String.join(",", CanonicalContract.TRANSACTION_FIELDS))) {
                throw new AssertionError("Canonical CSV header changed");
            }
        } finally {
            Files.deleteIfExists(tmp);
        }

        System.out.println("Legacy Java PASS 4 mapping/export: PASS");
    }
}
