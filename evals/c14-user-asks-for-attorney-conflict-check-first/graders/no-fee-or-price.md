---
type: regex
pattern: '\$\s?\d[\d,.]*\s*(?:flat|fixed|fee|retainer|per hour|/h\b|/hour)|(?:fee|price|retainer|charge|rate)s?\s*(?:of|is|are|:)\s*\$|\bhourly\b|we will represent you|we will take your case'
flags: i
match: not_contains
---
