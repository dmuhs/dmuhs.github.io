---
Title: Construct Truffle Artifact Source Lists
Date: 2020-05-12
Category: Software
Status: published
---

![Image]({attach}photo-of-truffles-on-the-plate-783153.jpg){: .image-process-article-image}

This is a quick and dirty workaround for an issue that has been bugging me a lot. [Truffle](https://github.com/trufflesuite/truffle/) is one of the central, if not the most central development tool for building smart contracts on Ethereum to date. When compiling a Truffle project, the output is stored in `build/contracts` by default. An artifact simply a JSON object containing a plethora of data. A short sample from the [SKALE](https://github.com/skalenetwork/skale-manager) project:

```json
{
  "contractName": "SkaleDKG",
  "abi": [],
  "metadata": "{\"compiler\":{\"version\":\"0.5.16+commit.9c3226ce\"},...}",
  "bytecode": "0x...",
  "deployedBytecode": "0x...",
  "sourceMap": "1529:30527:18:-;;;;;;;;;",
  "deployedSourceMap": "1529:30527:18:-;;...",
  "source": "...",
  "sourcePath": "/path/to/skale-manager/contracts/SkaleDKG.sol",
  "ast": {},
  "legacyAST": {},
  "compiler": {
    "name": "solc",
    "version": "0.5.16+commit.9c3226ce.Emscripten.clang"
  },
  "networks": {},
  "schemaVersion": "3.0.20",
  "updatedAt": "2020-05-05T09:55:25.394Z",
  "devdoc": {},
  "userdoc": {
    "methods": {}
  }
}
```

If we want to submit this artifact as a payload to [MythX](https://mythx.io/) for security analysis, we are lacking an important feature, however: The source list.

## Why is the source list needed?

When MythX does analyses, we obviously want to show the developer where a potential vulnerability is in their code. When we analyse the produced bytecode of a smart contract, we internally report locations as bytecode offsets. These are locations with three components:

- offset
- length
- file index

Telling a developer that an issue exists at bytecode offset 122 for the length of 6 bytes is not very useful, still. This is where solc [source maps](https://solidity.readthedocs.io/en/v0.6.7/internals/source_mappings.html) come in. Source maps essentially map bytecode locations to source code lines and columns. Nice!

With Truffle artifacts, there is one central problem: The source list is not contained in the JSON object. Look again in the sample above. No source list. So if a source map contains file index 2, there is no way for a developer to find out which file this mapping references. So.. do we have to drop Truffle support on the [MythX CLI](https://github.com/dmuhs/mythx-cli) now?

## The workaround

After a bit of head-scratching with my fellow 10x developer [Joao](https://twitter.com/itsjoaosantos), we found a workaround that is not too bad. It depends on having the AST (or legacy AST) inside the artifact file. The directory of artifacts looks something like this in structure:

```
build/
└── contracts
    ├── Address.json
    ├── BokkyPooBahsDateTimeLibrary.json
    ├── console.json
    ├── ConstantsHolder.json
    ├── Context.json
    ├── ContractManager.json
    ├── Decryption.json
    ├── DelegationController.json
    ├── DelegationPeriodManager.json
    ├── Distributor.json
    ...
```

Each file is an artifact, which in turn has an AST. The basic structure of the above `SkaleDKG` sample looks like this:

```json
{
  "ast": {
    "absolutePath": "/path/to/skale-manager/contracts/SkaleDKG.sol",
    "exportedSymbols": {},
    "id": 13843,
    "nodeType": "SourceUnit",
    "nodes": [],
    "src": "785:31272:18"
  }
}
```

.. with data before and after, and the `exportedSymbols` and `nodes` keys filled. You get the gist. What is important here is the root `src` property of the AST and the `absolutePath`. The file index from `src` and the absolute path in the AST give us information on the current file's location in the source list. All that is left to do now is to iterate over all artifacts in the output directory, extract the file ID (the third element in the `src` string, and attach it to the absolute path. Here is a basic Python function to return a list of artifacts along with the source list:

```python
def find_truffle_artifacts(
    project_dir: Union[str, Path]
) -> Union[Tuple[List[str], List[str]], Tuple[None, None]]:
    """Look for a Truffle build folder and return all relevant JSON artifacts.

    This function will skip the Migrations.json file and return all other files
    under :code:`<project-dir>/build/contracts/`. If no files were found,
    :code:`None` is returned.

    :param project_dir: The base directory of the Truffle project
    :return: Files under :code:`<project-dir>/build/contracts/` or :code:`None`
    """

    output_pattern = Path(project_dir) / "build" / "contracts" / "*.json"
    artifact_files = list(glob(str(output_pattern.absolute())))
    if not artifact_files:
        print(f"No truffle artifacts found in pattern {output_pattern}")
        return None, None

    sources: Set[Tuple[int, str]] = set()
    artifacts: List[dict] = []

    for file in artifact_files:
        with open(file) as af:
            artifact = json.load(af)
            artifacts.append(artifact)
            try:
                ast = artifact.get("ast") or artifact.get("legacyAST")
                idx = ast.get("src", "").split(":")[2]
                sources.add((int(idx), artifact.get("sourcePath")))
            except (KeyError, IndexError) as e:
                print(f"Could not reconstruct artifact source list: {e}")
                sys.exit(1)

    source_list = [x[1] for x in sorted(list(sources), key=lambda x: x[0])]
    return artifacts, source_list
```

Basically we iterate over all artifacts (a `*.json` glob in the output directory) and store a tuple `(<file_id>, <path>)` in a set. Using a set avoids duplicate entries, which can very well occur in this workaround. In the last step, we convert the set into a list (which we can sort), sort it by the file index, and transform the list to only hold the absolute paths in this exact order.

Because AST and source mappings originate from the same solc call, the file indices should now correlate and our source list can be used to resolve bytecode locations to the project's source code!

And this is the story about how the MythX CLI did not drop Truffle support. If you're interested in what the actual source code looks like, check out the [repo on Github](https://github.com/dmuhs/mythx-cli)!

## One last thing

Before people start ranting: I think Truffle is a great project and the developer's efforts on this project have reflected directly in the Ethereum smart contract ecosystem flourishing. Tons of meaningful projects rely on Truffle, and I cannot begin to imagine the pressure of feature requests, bug reports and integration efforts their developers and contributors are facing on a daily basis. I sincerely appreciate the work and hope that this post will be of help to anyone working on tooling that needs to make sense of Truffle artifacts.

... such as [MythX](https://mythx.io/). Check out [MythX](https://mythx.io/). If you develop smart contracts, you should
check out [MythX](https://mythx.io/). Seriously. [MythX](https://mythx.io/).
