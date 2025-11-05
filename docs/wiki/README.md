# SecAI Radar Wiki Documentation

This directory contains comprehensive wiki documentation for SecAI Radar, ready for GitHub Pages or GitHub Wiki.

---

## Using This Wiki

### Option 1: GitHub Wiki

1. **Enable GitHub Wiki** for your repository
2. **Copy these files** to the GitHub Wiki repository
3. **Edit in GitHub** or push directly to wiki repository

**GitHub Wiki Structure**:
- Files in `docs/wiki/` → GitHub Wiki pages
- `Home.md` → Wiki homepage
- Other pages → Linked from homepage

### Option 2: GitHub Pages

1. **Set up GitHub Pages** for your repository
2. **Use a static site generator** (Jekyll, MkDocs, etc.)
3. **Copy these files** to Pages source directory
4. **Build and deploy** via GitHub Actions

**Recommended**: Use [MkDocs](https://www.mkdocs.org/) or [GitBook](https://www.gitbook.com/) for better navigation.

---

## Wiki Pages

### User Documentation

- **[Home](Home.md)** - Wiki homepage and overview
- **[Getting Started](Getting-Started.md)** - Quick start guide
- **[User Guide](User-Guide.md)** - Complete user documentation
- **[Dashboard Guide](Dashboard-Guide.md)** - Dashboard usage
- **[Controls Guide](Controls-Guide.md)** - Controls management
- **[Tools Guide](Tools-Guide.md)** - Tools configuration
- **[Gaps Guide](Gaps-Guide.md)** - Gap analysis

### Technical Documentation

- **[Architecture](Architecture.md)** - System architecture
- **[API Reference](API-Reference.md)** - API documentation
- **[Installation](Installation.md)** - Installation guide
- **[Configuration](Configuration.md)** - Configuration guide

### Help & Support

- **[FAQ](FAQ.md)** - Frequently asked questions
- **[Troubleshooting](Troubleshooting.md)** - Common issues and solutions
- **[Glossary](Glossary.md)** - Terms and definitions

### Contributing

- **[Contributing](Contributing.md)** - Contributing guide

---

## Wiki Structure

```
docs/wiki/
├── Home.md                    # Homepage
├── Getting-Started.md          # Quick start
├── User-Guide.md              # User documentation
├── Dashboard-Guide.md         # Dashboard usage
├── Controls-Guide.md          # Controls management
├── Tools-Guide.md             # Tools configuration
├── Gaps-Guide.md              # Gap analysis
├── Architecture.md            # Architecture
├── API-Reference.md           # API docs
├── Installation.md            # Installation
├── Configuration.md           # Configuration
├── FAQ.md                     # FAQ
├── Troubleshooting.md         # Troubleshooting
├── Glossary.md                # Glossary
├── Contributing.md            # Contributing
└── README.md                  # This file
```

---

## Navigation

### Internal Links

All wiki pages use internal links:
- `[Home](Home.md)` - Links to Home page
- `[Getting Started](Getting-Started.md)` - Links to Getting Started page
- `[FAQ](FAQ.md)` - Links to FAQ page

### Cross-References

Pages reference each other:
- User Guide → Dashboard Guide, Controls Guide, etc.
- FAQ → Troubleshooting, Installation, etc.
- Architecture → Data Model, Model Integration

---

## Maintaining the Wiki

### Adding New Pages

1. **Create new `.md` file** in `docs/wiki/`
2. **Add to Home.md** navigation
3. **Link from related pages**
4. **Update README.md** if needed

### Updating Existing Pages

1. **Edit the `.md` file**
2. **Update links** if page renamed
3. **Test navigation** works
4. **Update related pages** if needed

### Best Practices

1. **Keep Updated**: Update wiki as application evolves
2. **Link Related**: Link related pages together
3. **Use Examples**: Include examples where helpful
4. **Be Clear**: Write clearly and concisely
5. **Test Links**: Verify all links work

---

## Publishing to GitHub Wiki

### Step 1: Enable Wiki

1. Go to repository Settings
2. Enable "Wikis" feature
3. Wiki repository will be created

### Step 2: Clone Wiki Repository

```bash
git clone https://github.com/your-org/secai-radar.wiki.git
cd secai-radar.wiki
```

### Step 3: Copy Files

```bash
# Copy all wiki files
cp -r ../secai-radar/docs/wiki/* .

# Commit and push
git add .
git commit -m "Add wiki documentation"
git push origin master
```

### Step 4: Verify

1. Go to repository Wiki tab
2. Verify all pages appear
3. Test navigation links
4. Check formatting

---

## Publishing to GitHub Pages

### Option 1: MkDocs

1. **Install MkDocs**:
   ```bash
   pip install mkdocs mkdocs-material
   ```

2. **Create `mkdocs.yml`**:
   ```yaml
   site_name: SecAI Radar Documentation
   nav:
     - Home: Home.md
     - Getting Started: Getting-Started.md
     - User Guide: User-Guide.md
     # ... other pages
   ```

3. **Build and Deploy**:
   ```bash
   mkdocs build
   mkdocs gh-deploy
   ```

### Option 2: Jekyll

1. **Set up Jekyll** for GitHub Pages
2. **Copy files** to `docs/` directory
3. **Configure navigation** in `_config.yml`
4. **Build and deploy** via GitHub Actions

---

## Contributing

See [Contributing](Contributing.md) for guidelines on contributing to the wiki.

---

**Last Updated**: 2025-01-15

