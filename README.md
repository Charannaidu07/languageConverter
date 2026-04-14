# 🚀 Universal Source-to-Source Compiler

A robust, multi-language Source-to-Source compiler built in Python, featuring a dark-themed Streamlit visualizer dashboard. This project translates code between languages like `minilang`, `C`, `C++`, and `Java`, effectively showcasing the theoretical concepts of compiler design by interactively visualizing every compilation phase.

## 🌟 Features

- **Interactive UI**: A modern dashboard powered by Streamlit that breaks down every stage of compilation.
- **Language Integration**: Seamlessly translate simple structured programs across Minilang, C, C++, and Java.
- **Full Compiler Pipeline**: Visually exposes the 6 canonical phases of compilation.

## 🛠️ The 6-Phase Pipeline

1. **Lexical Analysis (Scanner)**
   - Translates raw source code into structured lexical tokens (Identifiers, Keywords, Operators, etc).
2. **Syntax Analysis (Parser)**
   - Validates rules of grammar and dynamically constructs an Abstract Syntax Tree (AST).
3. **Semantic Analysis**
   - Validates type consistency, variables, and populates the symbol table.
4. **Intermediate Representation (IR)**
   - Lowers the AST into generic, architecture-independent Three-Address Code structures.
5. **Code Optimization**
   - Streamlines intermediate code by eliminating redundancies.
6. **Target Code Generation**
   - Explores the optimized structures (or AST directly) to output valid target code—managing appropriate structural wrappers like Java's `class Main()` or C++ namespaces.

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd pride
   ```

2. **Create a Virtual Environment (Recommended):**
   *Linux/macOS:*
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   *Windows:*
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Ensure Streamlit (and any other requirements) are installed:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Launch the interactive dashboard locally using Streamlit:

```bash
streamlit run app.py
```

### Navigating the App:
- Select your **Source Language** and **Target Language** from the dropdowns.
- Write or paste your source code in the input area.
- Click the **Compile & Translate** button.
- Expand each individual phase's accordion dropdown to inspect exactly what the compiler is doing under the hood!

## 📂 Architecture
- `app.py`: Streamlit frontend dashboard and primary entrypoint.
- `compiler_core/`: The core abstraction infrastructure
  - `lexer.py`, `tokens.py`: Lexical scanning
  - `parser.py`, `ast_nodes.py`: Syntax logic
  - `semantic.py`: Type handling and symbols
  - `ir_gen.py`, `ir.py`: Intermediate formats
  - `optimizer.py`: Code performance passes
  - `codegen.py`: Final syntax emitting module
