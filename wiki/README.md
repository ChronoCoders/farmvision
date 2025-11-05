# FarmVision Wiki Pages

This directory contains all wiki pages for the FarmVision GitHub repository.

## 📁 Wiki Pages

### Core Documentation
- **Home.md** - Wiki home page with navigation
- **_Sidebar.md** - Wiki sidebar navigation menu
- **Installation-Guide.md** - Complete installation instructions
- **Quick-Start.md** - 5-minute quick start guide
- **Roadmap.md** - Project roadmap and future plans

### How to Upload to GitHub Wiki

GitHub Wiki is a separate git repository. Follow these steps to upload the wiki pages:

## Method 1: GitHub Web Interface (Easiest)

1. Go to your repository: https://github.com/ChronoCoders/farmvision
2. Click on the **Wiki** tab
3. Click **Create the first page** (if new) or **New Page**
4. For each wiki page:
   - Copy content from the `.md` file
   - Paste into the wiki editor
   - Use the filename (without .md) as the page title
   - Click **Save Page**

### Pages to Create (in this order):
1. Home (from Home.md)
2. Installation-Guide (from Installation-Guide.md)
3. Quick-Start (from Quick-Start.md)
4. Roadmap (from Roadmap.md)
5. _Sidebar (from _Sidebar.md) - This creates the sidebar navigation

## Method 2: Clone Wiki Repository (Advanced)

GitHub Wiki is a separate git repository that can be cloned:

```bash
# Clone the wiki repository
git clone https://github.com/ChronoCoders/farmvision.wiki.git
cd farmvision.wiki

# Copy wiki files
cp ../farmvision/wiki/*.md .

# Commit and push
git add .
git commit -m "Add initial wiki pages"
git push origin master
```

## Method 3: Script Upload (Automated)

Use the provided script to upload all wiki pages at once:

```bash
# From farmvision directory
cd wiki
chmod +x upload_wiki.sh
./upload_wiki.sh
```

(Note: Script requires GitHub CLI - `gh` - to be installed and authenticated)

---

## 📝 Wiki Page Structure

### Home.md
- Main landing page for the wiki
- Navigation to all other pages
- Project status and overview
- Quick links

### Installation-Guide.md
- Detailed installation instructions
- Platform-specific guides (Windows, Linux, macOS)
- Docker installation
- Troubleshooting section

### Quick-Start.md
- 5-minute setup guide
- Essential commands
- First steps tutorial
- Quick reference

### Roadmap.md
- Current version features
- Planned features by version
- Development priorities
- How to contribute

### _Sidebar.md
- Navigation menu shown on all wiki pages
- Organized by category
- Quick access to important pages
- External links

---

## 🔄 Updating Wiki Pages

To update wiki pages after initial upload:

### Option A: Edit on GitHub
1. Navigate to the wiki page on GitHub
2. Click **Edit**
3. Make changes
4. Click **Save Page**

### Option B: Clone and Update
```bash
# Clone wiki repo
git clone https://github.com/ChronoCoders/farmvision.wiki.git
cd farmvision.wiki

# Make changes to files
nano Home.md

# Commit and push
git add Home.md
git commit -m "Update Home page"
git push origin master
```

---

## 📋 Wiki Best Practices

### 1. Consistent Formatting
- Use headers (# ## ###) for structure
- Include table of contents for long pages
- Use code blocks with language tags
- Add screenshots for visual guidance

### 2. Internal Links
- Link between wiki pages: `[Page Name](Page-Name)`
- Use relative links
- Keep navigation consistent

### 3. External Links
- Link to repo files when relevant
- Link to issues/PRs for context
- Include version-specific links

### 4. Keep Updated
- Update wiki when releasing new versions
- Keep screenshots current
- Archive outdated information
- Mark pages with last update date

### 5. Organization
- Group related pages
- Use clear, descriptive titles
- Maintain sidebar navigation
- Create redirects for moved pages

---

## 🎯 Future Wiki Pages

Additional pages to create:

### User Documentation
- [ ] User-Guide.md - Complete user manual
- [ ] Drone-Project-Management.md - Managing projects
- [ ] Object-Detection.md - Detection features
- [ ] System-Monitoring.md - Monitoring guide
- [ ] Map-Visualization.md - Maps and visualization

### Developer Documentation
- [ ] API-Documentation.md - API reference
- [ ] Architecture.md - System architecture
- [ ] Database-Schema.md - Database models
- [ ] Development-Setup.md - Dev environment
- [ ] Contributing-Guide.md - Contribution guide

### Advanced Topics
- [ ] YOLOv8-Integration.md - AI model config
- [ ] WebODM-Integration.md - Orthophoto processing
- [ ] GIS-Processing.md - GIS data handling
- [ ] Performance-Optimization.md - Optimization tips
- [ ] Security.md - Security practices

### Deployment
- [ ] Production-Deployment.md - Production setup
- [ ] Docker-Deployment.md - Docker production
- [ ] Nginx-Configuration.md - Nginx setup
- [ ] SSL-TLS-Setup.md - HTTPS config
- [ ] Monitoring-Logging.md - Production monitoring

### Project Management
- [ ] Release-Notes.md - Version history
- [ ] Known-Issues.md - Current issues
- [ ] FAQ.md - Frequently asked questions

---

## 📞 Questions?

If you have questions about the wiki:
- Open an issue: https://github.com/ChronoCoders/farmvision/issues
- Start a discussion: https://github.com/ChronoCoders/farmvision/discussions
- Email: support@farmvision.com

---

**Last Updated:** January 2025
**Wiki Version:** 1.0.0
