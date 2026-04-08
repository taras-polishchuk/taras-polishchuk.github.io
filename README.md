# 👋 Taras Polishchuk — Frontend / Layout Developer Portfolio

> A personal portfolio website and collection of real-world layout projects, built to showcase front-end development skills to potential clients and employers.

🌐 **Live site:** [taras-polishchuk.github.io](https://taras-polishchuk.github.io)

---

## 📌 About

This repository is the source code of my personal developer portfolio — a one-page website that presents my skills, work experience, and completed projects. It also serves as a host for several standalone layout projects built as part of the portfolio showcase.

If you're looking for a **layout developer** who writes clean HTML/CSS, works with JavaScript, and can turn a design into a pixel-perfect, responsive website — you're in the right place.

---

## 🗂 Project Structure

```
taras-polishchuk.github.io/
│
├── index.html              # Main portfolio page
├── policy.html             # Privacy policy page
│
├── css/
│   └── style.min.css       # Compiled & minified styles for the main portfolio
│
├── js/
│   ├── script.js           # Main portfolio interactivity (menu, effects, mailer, scroll)
│   └── codewars.js         # Codewars stats widget
│
├── mailer/
│   ├── smart.php           # PHP backend for the contact form
│   └── phpmailer/          # PHPMailer library (email delivery)
│
├── img/                    # Images for the main portfolio
├── icons/                  # Icon assets
│
├── cv/                     # Interactive CV / Resume page
├── pulse/                  # "Pulse" — standalone layout project (with SASS)
├── autoenterprise/         # "AutoEnterprise" — corporate website layout project
├── food/                   # "Food" — restaurant/food landing layout project
├── goddest/                # "Goddest" — landing page layout project
├── monblan/                # "Monblan" — landing page layout project
├── uber/                   # "Uber" — landing page layout project
└── uberem/                 # "Uberem" — cleaning services company website
```

---

## ✨ Portfolio Features

The main `index.html` portfolio page includes:

- 🧭 **Smooth navigation** — hamburger mobile menu with overlay and animated close
- 🎨 **Skills section** — visual progress bars showing tech proficiency levels
- 🖼 **Portfolio gallery** — CSS grayscale filter hover effects on project thumbnails
- 💌 **Contact form** — Ajax-powered form that sends email via PHPMailer (no page reload)
- ⬆️ **Scroll-to-top button** — appears after scrolling down, smooth animated scroll back
- 📱 **Fully responsive** — mobile-first layout

---

## 🗂 Included Layout Projects

Each sub-folder is a self-contained website layout built from a design mockup:

| Project | Folder | Description |
|---|---|---|
| **Pulse** | `/pulse` | Multi-section landing page (uses SASS for styles) |
| **AutoEnterprise** | `/autoenterprise` | Corporate website for an auto business |
| **Food** | `/food` | Restaurant / food delivery landing page |
| **Goddest** | `/goddest` | Stylish goods/lifestyle landing page |
| **Monblan** | `/monblan` | Product landing page |
| **Uber** | `/uber` | Uber-inspired landing page layout |
| **Uberem** | `/uberem` | Cleaning services company website with work examples and service explanations |
| **CV** | `/cv` | Interactive résumé page with scroll-triggered skill animations |

---

## 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| **HTML5** | Semantic page structure |
| **CSS3 / SASS** | Styling, animations, responsive layout |
| **JavaScript (ES6+)** | DOM manipulation, interactivity |
| **jQuery** | Ajax form submission, scroll utilities |
| **PHP + PHPMailer** | Server-side contact form email delivery |

---

## 📬 Contact Form

The portfolio includes a working contact form. Messages are sent to the developer's email address via a PHP backend using the **PHPMailer** library.

The form submits asynchronously (no page reload) using jQuery Ajax:

```javascript
$('form').submit(function(e) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: "mailer/smart.php",
        data: $(this).serialize()
    }).done(function() {
        $('form').trigger('reset');
    });
});
```

> ⚠️ To use the contact form locally, you need a PHP server (e.g. XAMPP, WAMP, or a hosting provider).

---

## 🚀 Getting Started

### View Online

Just open the live site: **[taras-polishchuk.github.io](https://taras-polishchuk.github.io)**

### Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/taras-polishchuk/taras-polishchuk.github.io.git
   ```

2. **Open in browser:**
   ```bash
   # For static browsing (no contact form):
   open index.html
   ```

3. **For full functionality (contact form):**
   - Set up a local PHP server (e.g. XAMPP or WAMP)
   - Place the project in the server's `htdocs` / `www` directory
   - Access via `http://localhost/taras-polishchuk.github.io/`

---

## 📁 Individual Projects

To view any of the sub-projects, navigate to their folder in your browser or open the hosted version:

- `https://taras-polishchuk.github.io/pulse/`
- `https://taras-polishchuk.github.io/autoenterprise/`
- `https://taras-polishchuk.github.io/food/`
- `https://taras-polishchuk.github.io/cv/`
- *(and so on for each subfolder)*

---

## 👤 Author

**Taras Polishchuk** — Frontend / Layout Developer

- GitHub: [@taras-polishchuk](https://github.com/taras-polishchuk)
- Portfolio: [taras-polishchuk.github.io](https://taras-polishchuk.github.io)

---

*Feel free to explore the code, get inspired, or reach out if you're looking for a layout developer!* 🚀