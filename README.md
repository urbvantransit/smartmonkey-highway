# smartmonkey-highway

## Usage

rename the `.env.sample` file to `.env` and set the private token

```python
from highway import Plan


plan_id = "34f2783fd2652002fb83733"
# get plan
my_plan = Plan.retrieve(plan_id)
# update plan
Plan.update(plan_id, data={"external_id":"123"})
```

## Test

```bash
pytest
```
