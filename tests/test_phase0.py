import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"engine"))
from validate import validate
import simulate

class TestPhase0(unittest.TestCase):
    def test_validate_passes(self):
        self.assertEqual(validate(), [], validate())
    def test_duplicate_prevention(self):
        state={"last_processed_date":"0001-01-01"}
        with self.assertRaises(RuntimeError):
            simulate.process_day(state, "0001-01-01")
    def test_no_undiscovered_in_known_recipes(self):
        materials={m["id"]:m for m in json.loads((ROOT/"world"/"materials.json").read_text(encoding="utf-8"))}
        recipes=json.loads((ROOT/"world"/"recipes.json").read_text(encoding="utf-8"))
        for r in recipes:
            if r["status"] in ("known","researching"):
                for m in r["materials"]:
                    self.assertEqual(materials[m["material_id"]]["discovery_status"],"discovered")

if __name__=="__main__":
    unittest.main()
