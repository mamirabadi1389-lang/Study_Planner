<div align="center">

<img src="assets/planner-preview.png" alt="Study Planner" width="900">

<br><br>

# STUDY PLANNER

### Modern desktop study planning application

<br>

<a href="#english">
  <img src="https://img.shields.io/badge/ENGLISH-111111?style=for-the-badge">
</a>
&nbsp;
<a href="#فارسی">
  <img src="https://img.shields.io/badge/فارسی-111111?style=for-the-badge">
</a>

<br><br>

<img src="https://img.shields.io/badge/Python-3.12-111111?style=flat-square&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/HTML5-111111?style=flat-square&logo=html5&logoColor=white">
<img src="https://img.shields.io/badge/CSS3-111111?style=flat-square&logo=css3&logoColor=white">
<img src="https://img.shields.io/badge/JavaScript-111111?style=flat-square&logo=javascript&logoColor=white">
<img src="https://img.shields.io/badge/pywebview-111111?style=flat-square">

<br><br>

> **Plan smarter. Study better. Stay organized.**

</div>

---

<a name="english"></a>

# 🇬🇧 English

<div align="center">

## ✦ About the Project

</div>

**Study Planner** is a modern desktop application built to make study planning and academic task management easier.

The application combines a web-based interface with a native desktop environment using **Python and pywebview**, providing a clean and focused experience without requiring a traditional browser window.

<br>

<div align="center">

|    📅 Planning    |       ✅ Tasks      |      📊 Organization      |
| :---------------: | :----------------: | :-----------------------: |
| Build study plans | Manage study tasks | Keep everything organized |

</div>

---

## ⚡ Features

<table>
<tr>
<td width="50%">

### 📅 Study Planning

Create and organize your study schedule in one place.

</td>
<td width="50%">

### ✅ Task Management

Keep track of academic tasks and study sessions.

</td>
</tr>

<tr>
<td>

### 🖥️ Desktop Experience

Runs as a dedicated Windows application using pywebview.

</td>
<td>

### ⚡ Lightweight

Designed to provide a simple and focused experience.

</td>
</tr>

<tr>
<td>

### 📦 Standalone Build

Can be compiled into a standalone Windows application using Nuitka.

</td>
<td>

### 🎨 Custom UI

Custom interface and application branding.

</td>
</tr>
</table>

---

## 🧠 Tech Stack

<div align="center">

| Technology     | Purpose                   |
| :------------- | :------------------------ |
| **Python**     | Application logic         |
| **HTML**       | User interface structure  |
| **CSS**        | Interface styling         |
| **JavaScript** | Front-end interactions    |
| **pywebview**  | Desktop application layer |
| **Nuitka**     | Windows executable build  |
| **Inno Setup** | Windows installer         |

</div>

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │    Study Planner    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Python         │
                    │   Application Core  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      pywebview      │
                    │    Desktop Layer    │
                    └──────────┬──────────┘
                               │
              ┌────────────────▼────────────────┐
              │                                 │
        ┌─────▼─────┐                    ┌──────▼─────┐
        │    HTML   │                    │     CSS    │
        │     UI    │                    │   Styling  │
        └─────┬─────┘                    └──────┬─────┘
              │                                 │
              └────────────────┬────────────────┘
                               │
                        ┌──────▼──────┐
                        │ JavaScript  │
                        │ Interaction │
                        └─────────────┘
```

---

## 📁 Project Structure

```text
study_planner/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/
│
├── assets/
│   └── planner-preview.png
│
├── tools/
│   └── build_exe.py
│
├── build/
│
├── run.py
├── Planner.iss
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd study_planner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python run.py
```

---

## 📦 Build for Windows

The project uses **Nuitka** to create a standalone Windows build.

```bash
python tools/build_exe.py
```

The generated application will be located at:

```text
build/run.dist/Planner.exe
```

---

## 🧰 Create Installer

The Windows installer is configured with:

```text
Planner.iss
```

Open the file using **Inno Setup** and compile it.

The resulting installer will be generated in:

```text
installer/
```

---

## 🖼️ Preview

<div align="center">

<img src="assets/planner-preview.png" alt="Study Planner Preview" width="850">

<br><br>

**Clean interface · Focused workflow · Desktop experience**

</div>

---

## 📌 Status

<div align="center">

### 🟡 In Development

Study Planner is an ongoing project and new features and improvements are being added over time.

</div>

---

<a name="فارسی"></a>

# 🇮🇷 فارسی

<div align="center">

## ✦ درباره پروژه

</div>

**Study Planner** یک برنامه دسکتاپ مدرن برای برنامه‌ریزی مطالعه و مدیریت وظایف درسی است.

این پروژه با ترکیب **Python، HTML، CSS، JavaScript و pywebview** یک رابط کاربری وب را در قالب یک برنامه دسکتاپ ویندوزی اجرا می‌کند.

هدف اصلی پروژه ایجاد یک محیط ساده، مرتب و متمرکز برای مدیریت برنامه مطالعه است.

<br>

<div align="center">

|   📅 برنامه‌ریزی   |    ✅ وظایف   |    📊 سازمان‌دهی    |
| :----------------: | :----------: | :-----------------: |
| ساخت برنامه مطالعه | مدیریت وظایف | مرتب‌سازی فعالیت‌ها |

</div>

---

## ⚡ امکانات

<table>
<tr>
<td width="50%">

### 📅 برنامه‌ریزی مطالعه

برنامه‌های مطالعه خود را در یک محیط منظم مدیریت کنید.

</td>
<td width="50%">

### ✅ مدیریت وظایف

وظایف درسی و جلسات مطالعه را مدیریت کنید.

</td>
</tr>

<tr>
<td>

### 🖥️ تجربه دسکتاپ

برنامه به صورت یک اپلیکیشن اختصاصی ویندوزی اجرا می‌شود.

</td>
<td>

### ⚡ سبک و سریع

تمرکز پروژه روی یک تجربه ساده و کاربردی است.

</td>
</tr>

<tr>
<td>

### 📦 نسخه مستقل

امکان ساخت نسخه مستقل Windows با استفاده از Nuitka وجود دارد.

</td>
<td>

### 🎨 رابط اختصاصی

رابط کاربری و هویت بصری اختصاصی برای برنامه طراحی شده است.

</td>
</tr>
</table>

---

## 🧠 تکنولوژی‌ها

<div align="center">

| تکنولوژی       | کاربرد                    |
| :------------- | :------------------------ |
| **Python**     | منطق اصلی برنامه          |
| **HTML**       | ساختار رابط کاربری        |
| **CSS**        | طراحی و ظاهر رابط         |
| **JavaScript** | تعاملات رابط کاربری       |
| **pywebview**  | اجرای رابط در محیط دسکتاپ |
| **Nuitka**     | ساخت فایل اجرایی ویندوز   |
| **Inno Setup** | ساخت Installer            |

</div>

---

## 🏗️ معماری پروژه

```text
                    ┌─────────────────────┐
                    │    Study Planner    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │       Python        │
                    │    هسته برنامه     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      pywebview      │
                    │    لایه دسکتاپ      │
                    └──────────┬──────────┘
                               │
              ┌────────────────▼────────────────┐
              │                                 │
        ┌─────▼─────┐                    ┌──────▼─────┐
        │    HTML   │                    │     CSS    │
        │    رابط   │                    │    ظاهر    │
        └─────┬─────┘                    └──────┬─────┘
              │                                 │
              └────────────────┬────────────────┘
                               │
                        ┌──────▼──────┐
                        │ JavaScript  │
                        │ تعاملات     │
                        └─────────────┘
```

---

## 📁 ساختار پروژه

```text
study_planner/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/
│
├── assets/
│   └── planner-preview.png
│
├── tools/
│   └── build_exe.py
│
├── build/
│
├── run.py
├── Planner.iss
├── requirements.txt
└── README.md
```

---

## 🚀 اجرای پروژه

### ۱. دریافت پروژه

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd study_planner
```

### ۲. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۳. اجرای برنامه

```bash
python run.py
```

---

## 📦 ساخت نسخه ویندوز

برای ساخت نسخه مستقل ویندوز از **Nuitka** استفاده شده است.

```bash
python tools/build_exe.py
```

فایل اصلی برنامه در این مسیر قرار می‌گیرد:

```text
build/run.dist/Planner.exe
```

---

## 🧰 ساخت Installer

تنظیمات Installer در فایل زیر قرار دارد:

```text
Planner.iss
```

فایل را با **Inno Setup** باز کرده و Compile کنید.

خروجی Installer در مسیر زیر قرار می‌گیرد:

```text
installer/
```

---

## 🖼️ تصویر برنامه

<div align="center">

<img src="assets/planner-preview.png" alt="تصویر Study Planner" width="850">

<br><br>

**رابط تمیز · workflow متمرکز · تجربه دسکتاپ**

</div>

---

## 📌 وضعیت پروژه

<div align="center">

### 🟡 در حال توسعه

پروژه Study Planner همچنان در حال توسعه است و امکانات و بهبودهای جدید به آن اضافه می‌شوند.

</div>

---

<div align="center">

<br>

# STUDY PLANNER

### Plan smarter. Study better.

<br>

**Made with Python**

</div>
