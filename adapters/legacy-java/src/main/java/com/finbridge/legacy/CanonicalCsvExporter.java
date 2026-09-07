package com.finbridge.legacy;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Deterministic CSV transport exporter. */
public final class CanonicalCsvExporter {
    private CanonicalCsvExporter() {}

    public static void write(Path output, List<CanonicalTransaction> rows) throws IOException {
        List<String> lines = new ArrayList<>(rows.size() + 1);
        lines.add(String.join(",", CanonicalContract.TRANSACTION_FIELDS));
        for (CanonicalTransaction row : rows) {
            lines.add(String.join(",",
                csv(row.transactionId()),
                csv(row.accountId()),
                csv(row.bookingDate()),
                csv(row.amount().toPlainString()),
                csv(row.currency()),
                csv(row.direction()),
                csv(row.counterparty()),
                csv(row.sourceSystem())
            ));
        }
        Files.writeString(output, String.join("\n", lines) + "\n", StandardCharsets.UTF_8);
    }

    private static String csv(String value) {
        if (value.indexOf(',') < 0 && value.indexOf('"') < 0 && value.indexOf('\n') < 0 && value.indexOf('\r') < 0) {
            return value;
        }
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
