package com.finbridge.legacy;

import java.nio.file.Path;
import java.util.List;

/** PASS 4 executable legacy-to-canonical compatibility adapter. */
public final class LegacyAdapterApp {
    private LegacyAdapterApp() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new IllegalArgumentException("Usage: LegacyAdapterApp <canonical-output.csv>");
        }
        List<CanonicalTransaction> canonical = LegacySyntheticSource.buildBatch().stream()
            .map(LegacyTransactionMapper::toCanonical)
            .toList();
        CanonicalCsvExporter.write(Path.of(args[0]), canonical);
        System.out.println("FinBridge Java legacy export: " + canonical.size() + " rows -> " + args[0]);
    }
}
