.PHONY: pass0 pass1 pass2 pass3 pass4 python-test java-test frontend-check azurite-smoke pass4-azurite-smoke

pass0:
	./scripts/pass0_gate.sh

pass1:
	./scripts/pass1_gate.sh

pass2:
	./scripts/pass2_gate.sh

pass3:
	./scripts/pass3_gate.sh

pass4:
	./scripts/pass4_gate.sh

python-test:
	./scripts/test_python.sh

java-test:
	./scripts/test_java.sh

frontend-check:
	./scripts/typecheck_frontend.sh

azurite-smoke:
	PYTHONPATH=services/domain:services/storage:services/processing python scripts/pass3_azurite_smoke.py

pass4-azurite-smoke:
	PYTHONPATH=services/domain:services/storage:services/processing python scripts/pass4_azurite_smoke.py artifacts/pass4/java-canonical.csv

pass7:
	./scripts/pass7_gate.sh
