# Data-Driven Document Generation

> Generate personalized documents, batch reports, exam variants, and data dashboards from external data sources.

---

## Pattern 1: CLI Inputs (`sys.inputs`)

Pass key-value pairs at compile time. No external file needed.

```bash
typst compile report.typ --input name="Alice" --input date="2026-02-25" --input score="92"
```

```typst
// In report.typ
#let name = sys.inputs.at("name", default: "Student")
#let score = sys.inputs.at("score", default: "N/A")

= Report for #name

Your score: #score / 100
```

**Use for:** Personalized cover pages, simple parameterization, CI/CD pipelines.

---

## Pattern 2: JSON/CSV Data Loading

Load structured data directly in Typst.

### JSON

```typst
#let students = json("students.json")

#for student in students [
  == #student.name
  - GPA: #student.gpa
  - Major: #student.major
]
```

```json
[
  {"name": "Alice", "gpa": 3.8, "major": "Finance"},
  {"name": "Bob", "gpa": 3.5, "major": "Economics"}
]
```

### CSV

```typst
#let data = csv("results.csv")
#let headers = data.first()

#table(
  columns: headers.len(),
  ..headers.map(h => [*#h*]),
  ..data.slice(1).flatten().map(cell => [#cell]),
)
```

### YAML

```typst
#let config = yaml("config.yaml")
```

**Use for:** Data tables, student rosters, grade reports, dashboards.

---

## Pattern 3: Batch Compilation

Generate multiple documents from different inputs using a shell script.

```bash
#!/bin/bash
# Generate personalized certificates for all students

while IFS=, read -r name course grade; do
  typst compile certificate.typ \
    --input name="$name" \
    --input course="$course" \
    --input grade="$grade" \
    "output/${name// /_}_certificate.pdf"
done < students.csv
```

Or with JSON data:

```bash
#!/bin/bash
# Generate reports from JSON array
jq -c '.[]' students.json | while read -r student; do
  name=$(echo "$student" | jq -r '.name')
  typst compile report.typ \
    --input data="$student" \
    "output/${name// /_}_report.pdf"
done
```

**Use for:** Certificates, personalized letters, batch grade reports.

---

## Pattern 4: Exam Variant Generation

Generate multiple exam versions with shuffled questions.

```typst
#let seed = int(sys.inputs.at("seed", default: "42"))
#let variant = sys.inputs.at("variant", default: "A")

#let questions = json("question-bank.json")

// Simple deterministic shuffle based on seed
#let shuffled = {
  let arr = questions
  let n = arr.len()
  // Use seed to pick a rotation offset
  let offset = calc.rem(seed, n)
  arr.slice(offset) + arr.slice(0, offset)
}

#align(center)[
  #text(size: 14pt, weight: "bold")[Exam — Variant #variant]
]

#for (i, q) in shuffled.enumerate() [
  #set enum(start: i + 1)
  + #q.text _(#q.marks marks)_
  #v(3cm)
]
```

```bash
# Generate 4 variants
for i in 1 2 3 4; do
  typst compile exam.typ --input seed="$i" --input variant="$(echo ABCD | cut -c$i)" \
    "exam_variant_$(echo ABCD | cut -c$i).pdf"
done
```

**Use for:** Exam variants, quiz randomization, assignment versions.

---

## When to Use Data-Driven Generation

| Scenario | Pattern | Data Source |
|----------|---------|-------------|
| Personalized cover page | `sys.inputs` | CLI args |
| Student roster table | JSON/CSV loading | Data file |
| Batch certificates | Shell script + `sys.inputs` | CSV file |
| Exam variants | JSON bank + seed shuffle | Question bank |
| Data dashboard | JSON/CSV loading | API export or database dump |
| Mail merge (letters) | Shell script + `sys.inputs` | Contact CSV |

---

## Tips

- Keep data files in the same directory as the `.typ` file (or use `--root` for parent access)
- JSON is preferred over CSV for structured/nested data
- Use `sys.inputs` for simple parameterization, JSON/CSV for bulk data
- For large datasets (1000+ rows), consider pre-processing with Python and passing summary JSON
- Always validate data structure: `#assert(students.len() > 0, message: "No student data found")`
