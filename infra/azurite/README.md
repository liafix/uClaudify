# Local Azurite boundary

PASS 3 uses the same Azure Blob SDK adapter for both real Azure Storage and Azurite.

```bash
docker compose -f infra/azurite/docker-compose.yml up -d
python -m pip install -r functions/azure/requirements.txt
PYTHONPATH=services/domain:services/storage:services/processing python scripts/pass3_azurite_smoke.py
```

The default connection string is `UseDevelopmentStorage=true`. The four containers are `raw`,
`processed`, `quarantine` and `audit`.
