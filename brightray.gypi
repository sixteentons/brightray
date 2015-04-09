{
  'includes': [
    'vendor/download/libchromiumcontent/filenames.gypi',
  ],
  'variables': {
    # Build with clang on Linux and Mac.
    'clang%': 1,

    'libchromiumcontent_src_dir': '<(libchromiumcontent_root_dir)/src',
    'libchromiumcontent_component%': 1,
    'conditions': [
      # The "libchromiumcontent_component" is defined when calling "gyp".
      ['libchromiumcontent_component', {
        'libchromiumcontent_dir%': '<(libchromiumcontent_root_dir)/shared_library',
        'libchromiumcontent_libraries%': '<(libchromiumcontent_shared_libraries)',
      }, {
        'libchromiumcontent_dir%': '<(libchromiumcontent_root_dir)/static_library',
        'libchromiumcontent_libraries%': '<(libchromiumcontent_static_libraries)',
      }],
    ],

    # See http://msdn.microsoft.com/en-us/library/aa652360(VS.71).aspx
    'win_release_Optimization%': '2', # 2 = /Os
    'win_debug_Optimization%': '0',   # 0 = /Od

    # See http://msdn.microsoft.com/en-us/library/2kxx5t2c(v=vs.80).aspx
    # Tri-state: blank is default, 1 on, 0 off
    'win_release_OmitFramePointers%': '0',
    # Tri-state: blank is default, 1 on, 0 off
    'win_debug_OmitFramePointers%': '',

    # See http://msdn.microsoft.com/en-us/library/8wtf2dfz(VS.71).aspx
    'win_debug_RuntimeChecks%': '3',    # 3 = all checks enabled, 0 = off

    # See http://msdn.microsoft.com/en-us/library/47238hez(VS.71).aspx
    'win_debug_InlineFunctionExpansion%': '',    # empty = default, 0 = off,
    'win_release_InlineFunctionExpansion%': '2', # 1 = only __inline, 2 = max
  },
  'target_defaults': {
    'includes': [
       # Rules for excluding e.g. foo_win.cc from the build on non-Windows.
      'filename_rules.gypi',
    ],
    # Putting this in "configurations" will make overrides not working.
    'xcode_settings': {
      'ALWAYS_SEARCH_USER_PATHS': 'NO',
      'ARCHS': ['x86_64'],
      'COMBINE_HIDPI_IMAGES': 'YES',
      'GCC_ENABLE_CPP_EXCEPTIONS': 'NO',
      'GCC_ENABLE_CPP_RTTI': 'NO',
      'GCC_TREAT_WARNINGS_AS_ERRORS': 'YES',
      'MACOSX_DEPLOYMENT_TARGET': '10.8',
      'RUN_CLANG_STATIC_ANALYZER': 'YES',
      'SDKROOT': 'macosx',
      'USE_HEADER_MAP': 'NO',
      'WARNING_CFLAGS': [
        '-Wall',
        '-Wextra',
        '-Wno-unused-parameter',
        '-Wno-missing-field-initializers',
      ],
    },
    'configurations': {
      # The "Debug" and "Release" configurations are not actually used.
      'Debug': {},
      'Release': {},

      'Common_Base': {
        'abstract': 1,
        'defines': [
          # We are using Release version libchromiumcontent:
          'NDEBUG',
          # From skia_for_chromium_defines.gypi:
          'SK_SUPPORT_LEGACY_GETTOPDEVICE',
          'SK_SUPPORT_LEGACY_BITMAP_CONFIG',
          'SK_SUPPORT_LEGACY_DEVICE_VIRTUAL_ISOPAQUE',
          'SK_SUPPORT_LEGACY_N32_NAME',
          'SK_SUPPORT_LEGACY_SETCONFIG',
          'SK_IGNORE_ETC1_SUPPORT',
          'SK_IGNORE_GPU_DITHER',
        ],
        'msvs_configuration_attributes': {
          'OutputDirectory': '<(DEPTH)\\build\\$(ConfigurationName)',
          'IntermediateDirectory': '$(OutDir)\\obj\\$(ProjectName)',
          'CharacterSet': '1',
        },
        'msvs_settings': {
          'VCLinkerTool': {
            'AdditionalDependencies': [
              'advapi32.lib',
              'dbghelp.lib',
              'dwmapi.lib',
              'gdi32.lib',
              'netapi32.lib',
              'oleacc.lib',
              'powrprof.lib',
              'user32.lib',
              'usp10.lib',
              'version.lib',
              'winspool.lib',
            ],
          },
        },
        'conditions': [
          ['OS!="mac"', {
            'defines': [
              'TOOLKIT_VIEWS',
              'USE_AURA',
            ],
          }],
          ['OS not in ["mac", "win"]', {
            'defines': [
              'USE_X11',
            ],
          }],
          ['OS=="linux"', {
            'cflags_cc': [
              '-D__STRICT_ANSI__',
              '-std=gnu++11',
              '-fno-rtti',
            ],
          }],  # OS=="linux"
        ],
      },  # Common_Base
      'Debug_Base': {
        'defines': [
          # Use this instead of "NDEBUG" to determine whether we are in
          # Debug build, because "NDEBUG" is already used by Chromium.
          'DEBUG',
          # Require when using libchromiumcontent.
          'COMPONENT_BUILD',
          'GURL_DLL',
          'SKIA_DLL',
          'USING_V8_SHARED',
          'WEBKIT_DLL',
        ],
        'msvs_settings': {
          'VCCLCompilerTool': {
            'RuntimeLibrary': '2',  # /MD (nondebug DLL)
            'Optimization': '<(win_debug_Optimization)',
            'BasicRuntimeChecks': '<(win_debug_RuntimeChecks)',
            'conditions': [
              # According to MSVS, InlineFunctionExpansion=0 means
              # "default inlining", not "/Ob0".
              # Thus, we have to handle InlineFunctionExpansion==0 separately.
              ['win_debug_InlineFunctionExpansion==0', {
                'AdditionalOptions': ['/Ob0'],
              }],
              ['win_debug_InlineFunctionExpansion!=""', {
                'InlineFunctionExpansion':
                  '<(win_debug_InlineFunctionExpansion)',
              }],
              # if win_debug_OmitFramePointers is blank, leave as default
              ['win_debug_OmitFramePointers==1', {
                'OmitFramePointers': 'true',
              }],
              ['win_debug_OmitFramePointers==0', {
                'OmitFramePointers': 'false',
                # The above is not sufficient (http://crbug.com/106711): it
                # simply eliminates an explicit "/Oy", but both /O2 and /Ox
                # perform FPO regardless, so we must explicitly disable.
                # We still want the false setting above to avoid having
                # "/Oy /Oy-" and warnings about overriding.
                'AdditionalOptions': ['/Oy-'],
              }],
            ],
          },
        },
      },  # Debug_Base
      'Release_Base': {
        'msvs_settings': {
          'VCCLCompilerTool': {
            'Optimization': '<(win_release_Optimization)',
            'conditions': [
              # According to MSVS, InlineFunctionExpansion=0 means
              # "default inlining", not "/Ob0".
              # Thus, we have to handle InlineFunctionExpansion==0 separately.
              ['win_release_InlineFunctionExpansion==0', {
                'AdditionalOptions': ['/Ob0'],
              }],
              ['win_release_InlineFunctionExpansion!=""', {
                'InlineFunctionExpansion':
                  '<(win_release_InlineFunctionExpansion)',
              }],
              # if win_release_OmitFramePointers is blank, leave as default
              ['win_release_OmitFramePointers==1', {
                'OmitFramePointers': 'true',
              }],
              ['win_release_OmitFramePointers==0', {
                'OmitFramePointers': 'false',
                # The above is not sufficient (http://crbug.com/106711): it
                # simply eliminates an explicit "/Oy", but both /O2 and /Ox
                # perform FPO regardless, so we must explicitly disable.
                # We still want the false setting above to avoid having
                # "/Oy /Oy-" and warnings about overriding.
                'AdditionalOptions': ['/Oy-'],
              }],
            ],
          },
        },
        'conditions': [
          ['OS=="linux"', {
            'cflags': [
              '-O2',
              # Generate symbols, will be stripped later.
              '-g',
              # Don't emit the GCC version ident directives, they just end up
              # in the .comment section taking up binary size.
              '-fno-ident',
              # Put data and code in their own sections, so that unused symbols
              # can be removed at link time with --gc-sections.
              '-fdata-sections',
              '-ffunction-sections',
            ],
            'ldflags': [
              # Specifically tell the linker to perform optimizations.
              # See http://lwn.net/Articles/192624/ .
              '-Wl,-O1',
              '-Wl,--as-needed',
              '-Wl,--gc-sections',
            ],
          }],  # OS=="linux"
        ],
      },  # Release_Base
      'conditions': [
        ['libchromiumcontent_component', {
          'D': {
            'inherit_from': ['Common_Base', 'Debug_Base'],
          },  # D (Debug)
        }, {
          'R': {
            'inherit_from': ['Common_Base', 'Release_Base'],
          },  # R (Release)
        }],  # libchromiumcontent_component
        ['OS=="win"', {
          'x64_Base': {
            'abstract': 1,
            'msvs_configuration_platform': 'x64',
            'msvs_settings': {
              'VCLinkerTool': {
                # Make sure to understand http://crbug.com/361720 if you want to
                # increase this.
                'MinimumRequiredVersion': '5.02',  # Server 2003.
                'TargetMachine': '17', # x86 - 64
                # Doesn't exist x64 SDK. Should use oleaut32 in any case.
                'IgnoreDefaultLibraryNames': [ 'olepro32.lib' ],
              },
              'VCLibrarianTool': {
                'TargetMachine': '17', # x64
              },
            },
          },  # x64_Base
        }],  # OS=="win"
        ['OS=="win" and libchromiumcontent_component==1', {
          'D_x64': {
            'inherit_from': ['Common_Base', 'x64_Base', 'Debug_Base'],
          },  # D_x64
        }],  # OS=="win" and libchromiumcontent_component==1
        ['OS=="win" and libchromiumcontent_component==0', {
          'R_x64': {
            'inherit_from': ['Common_Base', 'x64_Base', 'Release_Base'],
          },  # R_x64
        }],  # OS=="win" and libchromiumcontent_component==0
      ],
    },  # configurations
    'target_conditions': [
      # Putting this under "configurations" doesn't work.
      ['libchromiumcontent_component', {
        'xcode_settings': {
          'GCC_OPTIMIZATION_LEVEL': '0',
        },
      }, {  # "Debug_Base"
        'xcode_settings': {
          'DEAD_CODE_STRIPPING': 'YES',  # -Wl,-dead_strip
          'GCC_OPTIMIZATION_LEVEL': '2',
          'OTHER_CFLAGS': [
            '-fno-inline',
            '-fno-omit-frame-pointer',
            '-fno-builtin',
            '-fno-optimize-sibling-calls',
          ],
        },
      }],  # "Release_Base"
      ['OS=="mac" and libchromiumcontent_component==0 and _type in ["executable", "shared_library"]', {
        'xcode_settings': {
          # Generates symbols and strip the binary.
          'DEBUG_INFORMATION_FORMAT': 'dwarf-with-dsym',
          'DEPLOYMENT_POSTPROCESSING': 'YES',
          'STRIP_INSTALLED_PRODUCT': 'YES',
          'STRIPFLAGS': '-x',
        },
      }],  # OS=="mac" and libchromiumcontent_component==0 and _type in ["executable", "shared_library"]
      ['OS=="linux" and target_arch=="ia32" and _toolset=="target"', {
        'ldflags': [
          # Workaround for linker OOM.
          '-Wl,--no-keep-memory',
        ],
      }],
    ],  # target_conditions
  },  # target_defaults
  'conditions': [
    ['clang', {
      'make_global_settings': [
        ['CC', '/usr/bin/clang'],
        ['CXX', '/usr/bin/clang++'],
        ['LINK', '$(CXX)'],
        ['CC.host', '$(CC)'],
        ['CXX.host', '$(CXX)'],
        ['LINK.host', '$(LINK)'],
      ],
      'target_defaults': {
        'cflags_cc': [
          '-std=c++11',
        ],
        'xcode_settings': {
          'CC': '/usr/bin/clang',
          'LDPLUSPLUS': '/usr/bin/clang++',
          'OTHER_CFLAGS': [
            '-fcolor-diagnostics',
          ],

          'GCC_C_LANGUAGE_STANDARD': 'c99',  # -std=c99
          'CLANG_CXX_LIBRARY': 'libc++',  # -stdlib=libc++
          'CLANG_CXX_LANGUAGE_STANDARD': 'c++11',  # -std=c++11
        },
        'target_conditions': [
          ['_type in ["executable", "shared_library"]', {
            'xcode_settings': {
              # On some machines setting CLANG_CXX_LIBRARY doesn't work for
              # linker.
              'OTHER_LDFLAGS': [ '-stdlib=libc++' ],
            },
          }],
        ],
      },
    }],  # clang
    ['OS=="win"', {
      'target_defaults': {
        'include_dirs': [
          '<(libchromiumcontent_src_dir)/third_party/wtl/include',
        ],
        'defines': [
          '_WIN32_WINNT=0x0602',
          'WINVER=0x0602',
          'WIN32',
          '_WINDOWS',
          'NOMINMAX',
          'PSAPI_VERSION=1',
          '_CRT_RAND_S',
          'CERT_CHAIN_PARA_HAS_EXTRA_FIELDS',
          'WIN32_LEAN_AND_MEAN',
          '_ATL_NO_OPENGL',
          '_SECURE_ATL',
        ],
        'msvs_system_include_dirs': [
          '$(VSInstallDir)/VC/atlmfc/include',
        ],
        'msvs_settings': {
          'VCCLCompilerTool': {
            'AdditionalOptions': ['/MP'],
            'MinimalRebuild': 'false',
            'BufferSecurityCheck': 'true',
            'EnableFunctionLevelLinking': 'true',
            'RuntimeTypeInfo': 'false',
            'WarningLevel': '4',
            'WarnAsError': 'true',
            'DebugInformationFormat': '3',
          },
          'VCLinkerTool': {
            'GenerateDebugInformation': 'true',
            'MapFileName': '$(OutDir)\\$(TargetName).map',
            'ImportLibrary': '$(OutDir)\\lib\\$(TargetName).lib',
          },
        },
        'msvs_disabled_warnings': [
          4100, # unreferenced formal parameter
          4127, # conditional expression is constant
          4189, # local variable is initialized but not referenced
          4244, # 'initializing' : conversion from 'double' to 'size_t', possible loss of data
          4245, # 'initializing' : conversion from 'int' to 'const net::QuicVersionTag', signed/unsigned mismatch
          4251, # class 'std::xx' needs to have dll-interface.
          4310, # cast truncates constant value
          4355, # 'this' : used in base member initializer list
          4480, # nonstandard extension used: specifying underlying type for enum
          4481, # nonstandard extension used: override specifier 'override'
          4510, # default constructor could not be generated
          4512, # assignment operator could not be generated
          4610, # user defined constructor required
          4702, # unreachable code
          4819, # The file contains a character that cannot be represented in the current code page
        ],
      },
    }],
  ],
}
