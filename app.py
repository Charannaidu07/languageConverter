import streamlit as st
import traceback

from compiler_core.lexer import Lexer, LexerError
from compiler_core.parser import Parser, ParseError
from compiler_core.semantic import SemanticAnalyzer, SemanticError
from compiler_core.ir_gen import IRGenerator
from compiler_core.optimizer import Optimizer
from compiler_core.codegen import CodeGenerator

# UI Settings
st.set_page_config(page_title="Source-to-Source Compiler", layout="wide")

st.markdown("""
<style>
    .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        font-family: 'Fira Code', monospace !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
    }
    .phase-card {
        background: #161b22;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .phase-title {
        color: #00d4ff;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Universal Source-to-Source Compiler")
st.markdown("Transform source code across languages while visualizing all 6 canonical compiler phases.")

col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox("Source Language", ["minilang", "c", "cpp", "java"])
    
    default_code = ""
    if source_lang == "minilang":
         default_code = "let x = 10;\nlet y = 5;\nwhile (x > 0) {\n    print(y * 2);\n    x = x - 1;\n}\n"
    elif source_lang in ["c", "cpp"]:
         default_code = "int x = 10;\nint y = 5;\nwhile (x > 0) {\n    print(y * 2);\n    x = x - 1;\n}\n"
    else:
         default_code = "int x = 10;\nint y = 5;\nwhile (x > 0) {\n    print(y * 2);\n    x = x - 1;\n}\n"
         
    source_code = st.text_area("Source Code Input", height=300, value=default_code)

with col2:
    target_lang = st.selectbox("Target Language", ["python", "java", "c", "cpp", "minilang"])
    compile_btn = st.button("Compile & Translate", type="primary", use_container_width=True)
    st.markdown("---")
    
if compile_btn:
    try:
        # Phase 1: Lexical Analysis
        with st.expander("1. Lexical Analysis (Scanner)", expanded=False):
            lexer = Lexer(source_code, source_lang)
            tokens = lexer.tokenize()
            st.code("\n".join([repr(t) for t in tokens]), language="text")

        # Phase 2: Syntax Analysis
        with st.expander("2. Syntax Analysis (Parser)", expanded=False):
            parser = Parser(tokens)
            ast = parser.parse()
            st.success("AST generated successfully (check underlying structures).")
            
            from streamlit_agraph import agraph, Node, Edge, Config
            
            nodes = []
            edges = []
            
            def build_agraph_ast(node, parent_id=None, node_counter=None, link_label=""):
                if node_counter is None: node_counter = [0]
                current_id = f"N{node_counter[0]}"
                node_counter[0] += 1
                
                if isinstance(node, list):
                    if parent_id is None:
                        nodes.append(Node(id=current_id, label="Program", shape="box", color="#4CAF50", font={"color": "white"}))
                        parent_id = current_id
                    for i, child in enumerate(node):
                        build_agraph_ast(child, parent_id, node_counter, link_label=f"[{i}]")
                elif hasattr(node, '__dict__'):
                    label = node.__class__.__name__
                    for k, v in vars(node).items():
                        if v is None or isinstance(v, (str, int, float, bool)):
                            label += f"\n{k}: {v}"
                            
                    nodes.append(Node(id=current_id, label=label, shape="box", color="#1c2b36", font={"color": "white"}))
                    if parent_id:
                        edges.append(Edge(source=parent_id, label=link_label, target=current_id, color="#888"))
                        
                    for k, v in vars(node).items():
                        if not (v is None or isinstance(v, (str, int, float, bool))):
                            build_agraph_ast(v, current_id, node_counter, link_label=k)
                else:
                    label = str(node)
                    nodes.append(Node(id=current_id, label=label, shape="ellipse", color="#455a64", font={"color": "white"}))
                    if parent_id:
                        edges.append(Edge(source=parent_id, label=link_label, target=current_id, color="#888"))

            build_agraph_ast(ast)
            
            config = Config(
                width="100%",
                height=600,
                directed=True, 
                physics=True, 
                hierarchical=True,
                zoom=True,
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6",
            )
            
            if nodes:
                agraph(nodes=nodes, edges=edges, config=config)
            else:
                st.info("No AST generated.")

        # Phase 3: Semantic Analysis
        with st.expander("3. Semantic Analysis", expanded=False):
            semantic = SemanticAnalyzer()
            semantic.analyze(ast)
            st.success("Semantic checks passed. Symbol table verified.")
            st.code(str(semantic.symbol_table), language="json")

        # Phase 4: Intermediate Code Gen
        with st.expander("4. Intermediate Representation (Three-Address Code)", expanded=False):
            ir_gen = IRGenerator()
            ir_inst = ir_gen.generate(ast)
            st.code("\n".join([str(i) for i in ir_inst]), language="text")

        # Phase 5: Code Optimization
        with st.expander("5. Code Optimization", expanded=False):
            optimizer = Optimizer()
            optimized_ir = optimizer.optimize(ir_inst)
            st.code("\n".join([str(i) for i in optimized_ir]), language="text")

        # Phase 6: Code Gen (AST -> Target source code directly for structural accuracy)
        with st.expander("6. Target Code Generation", expanded=True):
            codegen = CodeGenerator(target_lang)
            target_code = codegen.generate(ast)
            st.code(target_code, language=target_lang if target_lang != "minilang" else "python")
            
        with col2:
            st.markdown("### Output")
            st.code(target_code, language=target_lang if target_lang != "minilang" else "python")
            
            if target_lang == "python":
                st.markdown("### Execution")
                import sys
                from io import StringIO
                import traceback
                
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                try:
                    # Provide an empty dict for globals so it doesn't mess with streamlit's scope
                    exec(target_code, {})
                    output = redirected_output.getvalue()
                    if output:
                        st.text_area("Console Output:", value=output, height=200)
                    else:
                        st.info("Program finished with no output.")
                except Exception as exec_e:
                    st.error(f"Execution Error")
                    st.code(traceback.format_exc(), language="text")
                finally:
                    sys.stdout = old_stdout

    except Exception as e:
        st.error(f"Compilation Error: {str(e)}")
        with st.expander("Detailed Traceback"):
            st.code(traceback.format_exc(), language="python")
