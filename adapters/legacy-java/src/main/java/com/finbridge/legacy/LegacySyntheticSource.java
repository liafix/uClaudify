package com.finbridge.legacy;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Deterministic synthetic source mirroring the frozen AlpineBank candidate-demo fixture. */
public final class LegacySyntheticSource {
    private LegacySyntheticSource() {}

    public static List<LegacyTransaction> buildBatch() {
        List<Integer> acceptedIds = new ArrayList<>();
        for (int value = 1; value <= 1021; value++) {
            if (value != 1011 && value != 1012) {
                acceptedIds.add(value);
            }
        }
        if (acceptedIds.size() != 1019) {
            throw new IllegalStateException("Frozen accepted-id generator changed");
        }

        List<LegacyTransaction> rows = new ArrayList<>();
        List<Integer> creditIds = acceptedIds.subList(0, 509);
        for (int index = 0; index < creditIds.size(); index++) {
            int id = creditIds.get(index);
            BigDecimal amount = index == 508 ? new BigDecimal("23800.00") : new BigDecimal("200.00");
            rows.add(buildValid(id, amount, "CR"));
        }

        List<Integer> debitIds = acceptedIds.subList(509, acceptedIds.size());
        for (int index = 0; index < debitIds.size(); index++) {
            int id = debitIds.get(index);
            BigDecimal amount = index == 509 ? new BigDecimal("22350.00") : new BigDecimal("150.00");
            rows.add(buildValid(id, amount, "DR"));
        }

        Map<String, LegacyTransaction> byId = new HashMap<>();
        for (LegacyTransaction row : rows) {
            byId.put(row.transactionRef(), row);
        }
        for (String duplicateId : List.of("TX-00482", "TX-00791", "TX-00902")) {
            LegacyTransaction original = byId.get(duplicateId);
            if (original == null) {
                throw new IllegalStateException("Missing frozen duplicate source " + duplicateId);
            }
            rows.add(original);
        }

        rows.add(new LegacyTransaction(
            "TX-01011", "ACC-011", "2026-09-05", new BigDecimal("10.00"), "EUX", "CR",
            "Synthetic Invalid Currency A"
        ));
        rows.add(new LegacyTransaction(
            "TX-01012", "ACC-012", "2026-09-05", new BigDecimal("20.00"), "EURO", "DR",
            "Synthetic Invalid Currency B"
        ));

        if (rows.size() != 1024) {
            throw new IllegalStateException("Synthetic Java batch has " + rows.size() + " rows instead of 1024");
        }
        return List.copyOf(rows);
    }

    private static LegacyTransaction buildValid(int id, BigDecimal amount, String movementCode) {
        return new LegacyTransaction(
            String.format("TX-%05d", id),
            String.format("ACC-%03d", (id % 17) + 1),
            "2026-09-05",
            amount,
            "EUR",
            movementCode,
            String.format("Synthetic Counterparty %04d", id)
        );
    }
}
