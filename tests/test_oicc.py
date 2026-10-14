"""Black-box regressions; all generated data stays in build/tests/.

Run: python tests/test_oicc.py --oicc build/mingw/x86_64/debug/oicc.exe
Requires a C11 gcc on PATH. No original oicc executable is invoked.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import os
import random
import re
import stat

ROOT = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--oicc", required=True)
parser.add_argument("--release", action="store_true")
args, rest = parser.parse_known_args()
EXE = (ROOT / args.oicc).resolve()


def run(command, cwd=ROOT):
    return subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=60)


def source(name, bases="OIOIC", members=""):
    return (f'#include "oioic.h"\n{members}\n'
            f'/* <oicc> */\n/* <ibn> {bases} </ibn> */\n'
            f'/* <crt> */\nold constructor\n/* </crt> */\n/* </oicc> */\n'
            f'void tog_{name}(struct object *object) {{ (void)object; }}\n')


class OiccTest(unittest.TestCase):
    def setUp(self):
        directory = ROOT / "build/tests"
        directory.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="case ", dir=directory)
        self.addCleanup(self.temp.cleanup)
        self.work = pathlib.Path(self.temp.name)

    def invoke(self, *arguments, success=True):
        result = run([EXE, *arguments])
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def write(self, name="a", bases="OIOIC", content=None):
        path = self.work / (name + ".c")
        path.write_text(source(name, bases) if content is None else content,
                        encoding="utf-8", newline="")
        return path

    def invalid(self, content, reason):
        path = self.write(content=content)
        before = path.read_bytes()
        result = self.invoke("generate", "--write", path, success=False)
        self.assertIn(reason, result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(list(self.work.glob("*.tmp")))

    def test_cli(self):
        self.invoke("--help")
        self.invoke("--version")
        for argv in [(), ("wat",), ("generate",), ("generate", "--write"),
                     ("new", "a"), ("check", "--wat")]:
            with self.subTest(argv=argv):
                self.assertEqual(self.invoke(*argv, success=False).returncode, 2)

    def test_new(self):
        path = self.work / "boat.c"
        self.invoke("new", "boat", path)
        before = path.read_bytes()
        self.invoke("new", "boat", path, success=False)
        self.assertEqual(before, path.read_bytes())
        self.invoke("check", path)
        self.invoke("generate", "--write", path)
        self.assertIn(b"crt_boat", path.read_bytes())
        for name, filename, bases in [("9x", "9x.c", "OIOIC"),
                                      ("a", "wrong.c", "OIOIC"),
                                      ("oioic", "oioic.c", "OIOIC"),
                                      ("a", "a.c", "OIOIC,"),
                                      ("a", "a.c", "OIOIC */ BAD")]:
            with self.subTest(name=name, bases=bases):
                dest = self.work / filename
                self.invoke("new", name, dest, bases, success=False)
                self.assertFalse(dest.exists())

    def test_preservation_and_idempotence(self):
        for newline in ["\n", "\r\n"]:
            with self.subTest(newline=newline):
                content = '// 中文 business\n' + source("a") + '// trailer\n'
                path = self.write(content=content.replace("\n", newline))
                before = path.read_bytes()
                self.invoke("check", path)
                self.invoke("generate", path)
                self.assertEqual(path.read_bytes(), before)
                self.invoke("generate", "--write", path)
                after = path.read_bytes()
                self.assertEqual(before.split(b"/* <crt> */")[0], after.split(b"/* <crt> */")[0])
                self.assertEqual(before.split(b"/* </crt> */")[1], after.split(b"/* </crt> */")[1])
                if newline == "\r\n":
                    self.assertNotIn(b"\n", after.replace(b"\r\n", b""))
                self.invoke("generate", "--write", path)
                self.assertEqual(after, path.read_bytes())

    def test_literals_and_comments(self):
        path = self.write(content='const char *s = "<oicc><ibn><crt></crt></ibn></oicc>";\n'
                          "int slash = '/'; /* ordinary comment */\n" + source("a"))
        self.invoke("check", path)
        self.invalid(source("a").replace("/* <crt> */", "// <crt>"), "standalone")
        self.invalid(source("a").replace("/* <crt> */", "/* x <crt> */"), "standalone")

    def test_broken_markers(self):
        variants = [source("a").replace("/* </crt> */", ""),
                    source("a") + "/* <oicc> */\n",
                    source("a").replace("<ibn> OIOIC </ibn>", "<ibn> OIOIC"),
                    source("a").replace("<ibn> OIOIC </ibn>", "<crt>"),
                    source("a").replace("/* <crt> */", "/* <crt> <crt> */")]
        for content in variants:
            with self.subTest(content=content):
                reason = "standalone" if "<crt> <crt>" in content else "ibn" if "<ibn> OIOIC */" in content else "marker"
                self.invalid(content, reason)

    def test_base_errors(self):
        for bases, reason in [("missing", "unknown"), ("a", "cycle"),
                              ("OIOIC,OIOIC", "duplicate direct"),
                              ("OIOIC,", "trailing"), ("OIOIC OIOIC", "comma"),
                              ("", "required"), ("9foo", "invalid")]:
            with self.subTest(bases=bases):
                self.invalid(source("a", bases), reason)

    def test_cycle_and_no_partial_writes(self):
        a = self.write("a", "b")
        b = self.write("b", "a")
        snapshots = [x.read_bytes() for x in (a, b)]
        self.invoke("generate", "--write", a, b, success=False)
        self.assertEqual(snapshots, [x.read_bytes() for x in (a, b)])
        b.write_text(source("b", "unknown"), encoding="utf-8")
        self.invoke("generate", "--write", a, b, success=False)
        self.assertEqual(a.read_bytes(), snapshots[0])
        self.assertFalse(list(self.work.glob("*.tmp")))

    def test_duplicate_nodes(self):
        a = self.write()
        self.invoke("check", a, a, success=False)
        directory = self.work / "other"
        directory.mkdir()
        other = directory / "A.c"
        other.write_text(source("A"), encoding="utf-8")
        result = self.invoke("check", a, other, success=False)
        self.assertIn("duplicate", result.stderr)

    def test_lexical_failures(self):
        for suffix, reason in [('/* unfinished', 'comment'), ('"unfinished', 'literal'),
                               ('\x00', 'NUL'), ('// splice \\\n', 'splicing')]:
            with self.subTest(reason=reason):
                self.invalid(source("a") + suffix, reason)
        path = self.write()
        path.write_bytes(path.read_bytes() + b"\xff")
        self.assertIn("UTF-8", self.invoke("check", path, success=False).stderr)
        self.invalid(source("a") + '// ??/\n', 'trigraph')
        self.invalid('%:if FLAG\n' + source("a") + '%:endif\n', 'digraph')

    def test_unsupported_declarations(self):
        self.invalid('#if FLAG\n' + source("a") + '#endif\n', "conditional")
        self.invalid(source("a", members='struct em_a { int x; }; struct em_a { int y; };'), "duplicate")
        self.invalid(source("a").replace("tog_a", "tog_other"), "binding")
        self.invalid(source("a", members='struct em_a __attribute__((aligned(32))) { int x; };'), "unsupported")
        self.invalid(source("a", members='#define DECL struct em_a { int x; };'), "macro")
        self.invalid(source("a", members='void local(void) { struct em_a { int x; }; }'), "unsupported")
        path = self.write()
        path.with_suffix(".h").write_text('#ifdef FLAG\nstruct em_a { int x; };\n#endif\n', encoding="utf-8")
        self.assertIn("conditional", self.invoke("check", path, success=False).stderr)
        path.with_suffix(".h").write_text('struct unrelated { int x; };\n#ifndef FEATURE\n#define FEATURE\nstruct em_a { int x; };\n#endif\n', encoding="utf-8")
        self.assertIn("conditional", self.invoke("check", path, success=False).stderr)
        path.with_suffix(".h").write_bytes(b'\xef\xbb\xbf#ifndef A_H\n#define A_H\nstruct em_a { int x; };\n#endif\n')
        self.invoke("check", path)

    def test_members_and_forward_graph(self):
        leaf = self.write("leaf", "left,right", source("leaf", "left,right", "struct em_leaf { int value; };"))
        left = self.write("left", "base")
        right = self.write("right", "base")
        base = self.write("base")
        self.invoke("generate", "--write", leaf, right, base, left)
        text = re.sub(r"\s+", " ", leaf.read_text(encoding="utf-8"))
        self.assertIn("OIOIC_ALIGNED_SIZE(struct em_leaf)", text)
        self.assertIn("direct_0[] = { 1, 4 }", text)
        self.assertIn("MSN_OIOIC, tog_oioic, OIOIC_ALIGNED_SIZE(struct em_oioic), _Alignof(struct em_oioic), 4", text)
        before = leaf.read_bytes()
        self.invoke("generate", "--write", base, leaf, left, right)
        self.assertEqual(before, leaf.read_bytes())

    def test_deep_graph(self):
        paths = [self.write(f"n{i}", f"n{i+1}" if i < 119 else "OIOIC") for i in range(120)]
        self.invoke("check", *paths)

    def test_random_dags_and_base_order(self):
        rng = random.Random(7331)
        graph = {f"g{i}": rng.sample([f"g{j}" for j in range(i + 1, 14)] + ["OIOIC"],
                                    min(3, 14 - i)) for i in range(14)}
        paths = [self.write(name, ",".join(bases)) for name, bases in graph.items()]
        self.invoke("generate", "--write", *reversed(paths))
        for name, path in zip(graph, paths):
            expected = []
            def visit(node):
                if node in expected:
                    return
                expected.append(node)
                for base in graph.get(node, []):
                    visit(base)
            visit(name)
            code = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
            bindings = re.findall(r"extern void tog_(\w+)", code)
            self.assertEqual(bindings, [node if node != "OIOIC" else "oioic" for node in expected])
            seats = {name: 1}
            def depth(node, value):
                seats[node] = max(seats.get(node, 0), value)
                for base in graph.get(node, []):
                    depth(base, value + 1)
            depth(name, 1)
            for node in expected:
                spelling = "oioic" if node == "OIOIC" else node
                match = re.search(r"\{ MSN_" + node.upper() + r", tog_" + spelling +
                                  r", .*?, (\d+), (?:direct_\d+|NULL),", code, re.S)
                self.assertIsNotNone(match, code)
                self.assertEqual(int(match.group(1)), seats[node])
        a = self.write("order_a", "g1,g2")
        b = self.write("order_b", "g2,g1")
        self.invoke("generate", "--write", a, b, *paths)
        self.assertEqual(re.findall(r"extern void tog_(\w+)", a.read_text())[1], "g1")
        self.assertEqual(re.findall(r"extern void tog_(\w+)", b.read_text())[1], "g2")

    def test_all_tool_allocation_failures(self):
        instrumented = self.work / "instrumented.exe"
        runtime = list((ROOT / "third_party/oioic/src").glob("*.c"))
        self.compile(instrumented, [*list((ROOT / "src").rglob("*.c")), *runtime,
                                   ROOT / "tests/tool_alloc.c"],
                     ["-include", ROOT / "tests/tool_alloc.h", "-I", ROOT / "tests"])
        path = self.write()
        before = path.read_bytes()
        result = run([instrumented, "generate", "--write", path])
        self.assertEqual(result.returncode, 0, result.stderr)
        total = int(re.search(r"test allocations: (\d+) live: 0", result.stderr).group(1))
        for failure in range(1, total + 1):
            with self.subTest(allocation=failure):
                path.write_bytes(before)
                env = os.environ.copy()
                env["OICC_TEST_FAIL_ALLOC"] = str(failure)
                result = subprocess.run([str(instrumented), "generate", "--write", str(path)],
                                        cwd=ROOT, env=env, capture_output=True, timeout=60)
                self.assertIn(b"live: 0", result.stderr)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse(list(self.work.glob("*.tmp")))

    def test_bootstrap_regeneration(self):
        copied = self.work / "src"
        shutil.copytree(ROOT / "src", copied)
        project = copied / "objects/project.c"
        before = project.read_bytes()
        self.invoke("generate", "--write", project)
        self.assertEqual(project.read_bytes(), before)
        tool = self.work / "bootstrap.exe"
        self.compile(tool, [*copied.rglob("*.c"), *list((ROOT / "third_party/oioic/src").glob("*.c"))])
        result = run([tool, "generate", "--write", project])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(project.read_bytes(), before)

    def test_host_lifecycle_and_interfaces(self):
        executable = self.work / "host.exe"
        files = [path for path in (ROOT / "src").rglob("*.c") if path.name != "main.c"]
        self.compile(executable, [*files, *list((ROOT / "third_party/oioic/src").glob("*.c")),
                                  ROOT / "tests/host.c"], ["-I", ROOT / "src"])
        result = run([executable])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_file_errors(self):
        self.invoke("check", self.work / "missing.c", success=False)
        self.invoke("new", "a", self.work / "missing/a.c", success=False)
        path = self.write()
        path.rename(path.with_suffix(".txt"))
        self.invoke("check", path.with_suffix(".txt"), success=False)
        directory = self.work / "directory.c"
        directory.mkdir()
        self.invoke("check", directory, success=False)

    @unittest.skipUnless(os.name == "nt", "Windows read-only replacement behavior")
    def test_windows_commit_failure_and_recovery(self):
        a = self.write("a")
        b = self.write("b")
        before_b = b.read_bytes()
        os.chmod(b, stat.S_IREAD)
        try:
            result = self.invoke("generate", "--write", a, b, success=False)
            self.assertIn("cannot replace file", result.stderr)
            self.assertIn("committed", result.stdout)
            self.assertIn(b"crt_a", a.read_bytes())
            self.assertEqual(b.read_bytes(), before_b)
            self.assertFalse(list(self.work.glob("*.tmp")))
        finally:
            os.chmod(b, stat.S_IWRITE)
        before_a = a.read_bytes()
        self.invoke("generate", "--write", a, b)
        self.assertEqual(a.read_bytes(), before_a)
        self.assertIn(b"crt_b", b.read_bytes())

    def compile(self, output, files, extra=()):
        result = run(["gcc", "-std=c11", "-O2" if args.release else "-O0",
                      *( ["-DNDEBUG"] if args.release else ["-g"] ),
                      "-I", ROOT / "third_party/oioic/include", "-I", ROOT / "include",
                      *extra, *files, "-o", output])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_reference_behavior_and_failures(self):
        reference = self.work / "reference"
        shutil.copytree(ROOT / "examples/oioic_reference", reference)
        nodes = [reference / f"so/go/{name}/{name}.c" for name in ("vehicle", "car", "ship", "amphicar")]
        runtime = list((ROOT / "third_party/oioic/src").glob("*.c"))
        original = self.work / "original.exe"
        application = [reference / "ho.c", reference / "Factory.c", reference / "so/ao/Main/Main.c"]
        self.compile(original, [*nodes, *runtime, *application])
        baseline = run([original])
        self.assertEqual(baseline.returncode, 0, baseline.stderr)
        self.assertEqual(len([line for line in baseline.stdout.splitlines() if line.strip()]), 11)
        self.invoke("generate", "--write", *nodes)
        generated = self.work / "generated.exe"
        self.compile(generated, [*nodes, *runtime, *application])
        result = run([generated])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, baseline.stdout)
        delegated = self.work / "delegated.exe"
        self.compile(delegated, [*nodes, *runtime, ROOT / "tests/delegation.c"], ["-I", reference])
        result = run([delegated])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        # Force allocations in constructors only through tracked wrappers.
        for path in nodes:
            path.write_text('#include "alloc.h"\n' + path.read_text(encoding="utf-8"), encoding="utf-8")
        harness = self.work / "harness.exe"
        self.compile(harness, [*nodes, *runtime, ROOT / "tests/runtime.c", ROOT / "tests/alloc.c"],
                     ["-I", reference, "-I", ROOT / "tests"])
        result = run([harness])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("runtime checks passed", result.stdout)


if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], *rest], verbosity=2)
