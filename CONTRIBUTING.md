# Contributing to Leo

Welcome! Here's how to contribute to Leo by adding new attack signatures or improving the codebase.

## Adding New Attack Signatures

### 1. Understand the Signature Format

Each signature in `leo_signatures.py` has this structure:

```python
"ATTACK_NAME": {
    "category": "CATEGORY",                          # Volumetric, Amplification, etc.
    "indicators": [("metric", "operator", value)],  # Detection indicators
    "confidence": 0.85,                             # Base confidence (0.0-1.0)
    "severity": Severity.HIGH,                      # CRITICAL, HIGH, MEDIUM
    "response": ResponseType.RATE_LIMIT,            # Block, Mitigate, Rate-Limit, Alert
    "description": "Attack description"
}
```

### 2. Create Your Attack Signature

Example: Adding a new HTTP-based attack

```python
"HTTP_HEADER_FLOOD": {
    "category": "APPLICATION",
    "indicators": [
        ("http_requests", ">", 10000),      # More than 10k requests/sec
        ("unique_paths", "<", 0.1),         # Less than 10% unique paths
        ("avg_header_size", ">", 5000)      # Large headers
    ],
    "confidence": 0.85,
    "severity": Severity.HIGH,
    "response": ResponseType.RATE_LIMIT,
    "description": "HTTP header flood attack"
}
```

### 3. Add Detection Logic

If your attack needs custom detection, add it to `leo_detector.py`:

```python
def detect_http_header_flood(self, metrics: Dict) -> float:
    """Detect HTTP header flood"""
    if metrics.get('http_requests', 0) > 10000:
        if metrics.get('unique_paths', 1) < 0.1:
            if metrics.get('avg_header_size', 0) > 5000:
                return 0.85
    return 0
```

### 4. Test Your Signature

Add test case in `leo_detector.py`:

```python
def test_http_header_flood(self):
    metrics = {
        'http_requests': 15000,
        'unique_paths': 0.05,
        'avg_header_size': 6000
    }
    result = self.detect_http_header_flood(metrics)
    assert result > 0.8
```

### 5. Add Metrics Collection

If metrics don't exist, add collection in `leo_detector.py`:

```python
def process_packet(self, packet):
    """Process packet"""
    # ... existing code ...
    
    # Add new metric tracking
    if HTTP in packet:
        self.http_requests += 1
        if len(packet[HTTP].payload) > self.avg_header_size:
            self.large_headers += 1
```

## Code Guidelines

### Style
- Use type hints on all functions
- Add docstrings to classes and methods
- Keep functions focused (single responsibility)
- Maximum line length: 100 characters

### Error Handling
```python
try:
    # Your code
except SpecificException as e:
    logger.error(f"Error: {e}")
    return None
```

### Logging
```python
logger.info("Normal operation")
logger.warning("Something unusual")
logger.error("Something failed")
logger.critical("Critical issue")
```

## File Structure

**To add a feature:**

1. **New metric calculation** → `leo_detector.py`
2. **New DPI rule** → `leo_dpi.py`
3. **New ML feature** → `leo_ml.py`
4. **New attack signature** → `leo_signatures.py`
5. **New geographic rule** → `leo_geo.py`

## Submitting Changes

1. Create a feature branch
```bash
git checkout -b add-http-header-flood
```

2. Make your changes
- Add signature to `leo_signatures.py`
- Add metrics to `leo_detector.py` if needed
- Add tests

3. Test thoroughly
```bash
# Run Leo with your changes
sudo leo start

# Monitor for errors
tail -f /var/log/leo-detection.log
```

4. Submit pull request with:
- Description of the attack
- Why it's important
- Detection method
- Test results

## Attack Signature Checklist

Before submitting, verify:

- [ ] Signature name is descriptive
- [ ] Category is correct
- [ ] Indicators make sense
- [ ] Confidence is realistic (0.0-1.0)
- [ ] Severity matches attack type
- [ ] Response type is appropriate
- [ ] Description is clear
- [ ] No duplicate signatures
- [ ] Metrics are collected
- [ ] Code has error handling
- [ ] Documentation updated

## Testing Your Signature

### Manual Testing

```bash
# Start Leo
sudo leo start

# In another terminal, simulate the attack
# (use your favorite network tools)

# Check if detected
grep "YOUR_ATTACK_NAME" /var/log/leo-incidents.jsonl
```

### Performance Testing

```bash
# Check detection time
leo performance

# Verify memory usage
ps aux | grep leo
```

## Common Mistakes

❌ **Too low confidence** - Creates false positives
✓ Set confidence >= 0.75 for signatures

❌ **No error handling** - Can crash detection
✓ Always use try/except blocks

❌ **Unclear indicators** - Hard to maintain
✓ Use clear metric names and operators

❌ **Complex signatures** - Slow detection
✓ Keep indicators list < 5 items

## Documentation

When adding a feature, update:

1. **leo_signatures.py** - Add description in signature
2. **README.md** - Add to attack coverage list
3. **LEO_DOCUMENTATION.md** - Add detailed info
4. **Code comments** - Explain the detection logic

## Questions?

Check existing signatures for examples:
```bash
grep -A 10 '"SYN_FLOOD"' leo_signatures.py
```

Review similar attacks:
```bash
grep -B 2 '"VOLUMETRIC"' leo_signatures.py
```

## Recognition

Contributors who add signatures will be listed in:
- CONTRIBUTORS.md
- GitHub releases
- Project documentation

Thank you for helping make Leo better! 🚀

---

**Leo - Help Us Detect More Attacks**
