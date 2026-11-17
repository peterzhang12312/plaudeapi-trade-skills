---
type: regex
pattern: 'https?://(?!plaudeapi\.com/)\S+|https?://plaudeapi\.com/(?!trade(?:[/\s)\].,;:*]|$))\S*|https?://plaudeapi\.com/trade/(?=[\w-])(?!(?:cf28|timeline|ieepa-refund|foreign-ior)(?:[^\w-]|$))'
match: not_contains
---
