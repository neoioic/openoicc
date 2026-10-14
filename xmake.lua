set_project("oicc")
set_languages("c11")
add_rules("mode.debug", "mode.release")
set_targetdir(path.join(os.scriptdir(), "build/$(plat)/$(arch)/$(mode)"))
set_objectdir(path.join(os.scriptdir(), "build/.objs/$(target)/$(plat)/$(arch)/$(mode)"))

includes("third_party/oioic/src")

-- The generator is not implemented yet. This target verifies the local runtime.
target("oioic_reference")
    set_kind("binary")
    set_default(false)
    add_deps("oioic")
    add_files("examples/oioic_reference/*.c", "examples/oioic_reference/so/**.c")
    set_warnings("all")
