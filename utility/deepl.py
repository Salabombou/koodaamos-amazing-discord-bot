import httpx
payload = {
    "jsonrpc": "2.0",
    "method": "LMT_handle_jobs",
    "params": {
        "jobs": [
            {
                "kind":
                    "default",
                    "sentences": [
                        {
                            "text": "terve maailma!",
                            "id": 0,
                            "prefix": ""
                        }
                    ],
                    "raw_en_context_before": [],
                    "raw_en_context_after": [],
                    "preferred_num_beams": 4
        }],
        "lang": {
            "preference": {
                "weight":{},
                "default":"default"
                },
            "source_lang_computed": "FI",
            "target_lang": "EN"
            },
        "priority": 1,
        "commonJobParams": {
            "browserType": 10241
            },
        "timestamp": 1656702859168},
    "id": 60630007}


async def translate(text):
    async with httpx.AsyncClient() as requests:
        r = requests.post()