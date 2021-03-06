# GitHub PR Form

A small python utility for generating forms from the command line and adding them to GitHub pull requests or issues, while tracking them in a secondary github repo.

## Use Case

This utility was developed to meet a change management security control, which requires RFC forms be included with pull requests to the production code base. However, it would be useful for any type of forms that need to be repeatably and reliably generated and added to GitHub pull requests. It should work equally well to add forms to GitHub issues.

## Requirements

- Python 2.6 or 2.7
    - github3, sh, click, markdown2, and selenium python packages, which should be installed automatically
- Firefox (for generation of PNG screenshots through selenium)

## Installation

Most Mac and Linux distributions should already have a compatible version of Python installed. Check your python installation by running `which python && python --version`. If you need to install Python, follow instructions at https://www.python.org/. Install or update Firefox at https://www.mozilla.org/firefox/new/.

Install the package with:

`pip install github-pr-form`

## Configuration

Where the phrase 'target repo' appears here, it refers to a repository whose pull requests will receive generated forms. Where the phrase 'tracking repo' appears, it refers to a repository used for tracking generated forms. More than one target repo may share a single tracking repo.

Both the target repo and tracking repo must be initialized and pushed to GitHub before configuration. The tracking repo should be empty to begin with and remain dedicated to the purpose of tracking forms. For the following examples, the fictional `octocat/target` and `octocat/tracking` will be used.

Generate a GitHub access token at https://github.com/settings/tokens/new with the 'repo' scope. For the examples, a fictional `XXXXXX` token will be used.

Form generation relies on templates (see the full discussion of template format [below](#template-format)). For the examples, a fictional `/Users/user/Desktop/rfc.json` template will be used.

Initialize a target repo with:

`ghform init --tracker=octact/tracking --token=XXXXXX octocat/target`

Add a template to the tracking repo with:

`ghform addtpl --tracker=octocat/tracking /Users/user/Desktop/rfc.json`

## General Usage

Generate a form and add it to a pull request with:

`ghform add --tpl=rfc octocat/target/pull/1`

The user will be prompted to respond to each field in a template and each response will be validated. If a response is determined to be invalid (see types of validity checks [below](#field-types-and-attributes)), an explanation is printed and the prompt is repeated. If a form from the given template already exists on the pull request, the existing responses will be set as defaults. Form generation may be aborted at any time with a `SIGINT` (`ctrl-c`). Response prompts are formatted simply and generally look like:

```markdown
Field Name
    field description
    options: a, b, c
    type [default]:

```

Once a form has been completed, it is saved in the tracking repo in `json`, `md`, `html`, and `png` formats. A comment is added on the pull request declaring that a form is about to be uploaded and linking to the `png` format. Another comment is added with the entire form in `md` format. If any actions (label application or user assignment, see [below](#field-types-and-attributes)) have been triggered, they are carried out. Note that if a form from from the same template has previously been added to the given pull request, the files in the tracking repo are overwritten (of course, they remain in the repo commit history).

## Example Usage

The [aaron0browne/github-pr-form-tracking](https://github.com/aaron0browne/github-pr-form-tracking) was set up as both a target and a tracking repo, which wouldn't make any sense in the real world, but is useful for this example. An issue was added to store uploaded images and another to receive a generated form (since there was no pull request to submit). The commands executed and results were:

`ghform init --tracker=aaron0browne/github-pr-form-tracking --token=XXXXXX aaron0browne/github-pr-form-tracking`

This command just wrote a local config file with the given information.

`ghform addtpl --tracker=aaron0browne/github-pr-form-tracking rfc.json`

This command added a `tpl` directory to the tracking repo and the example [rfc.json](ghform/rfc.json) template in that directory.

`ghform add --tpl=rfc aaron0browne/github-pr-form-tracking/issues/2`

This command kicked off the form response prompts at the command line:

![example-cli](https://cloud.githubusercontent.com/assets/3409975/5013229/25c2b544-6a5a-11e4-9571-4734dc109dbf.png)

Once all the prompts were completed, the form was formatted, converted, and saved as `json`, `md`, `html`, and `png` in the tracking repo:

![example-storage](https://cloud.githubusercontent.com/assets/3409975/5013238/31599422-6a5a-11e4-852b-4f8d7a76b903.png)

And two comments were added to the [target issue](https://github.com/aaron0browne/github-pr-form-tracking/issues/2) (the first comment was manually added when the issue was opened):

![example-result](https://cloud.githubusercontent.com/assets/3409975/5013236/2b81a8b4-6a5a-11e4-81b9-43be3d4bd713.png)

Note that the defined labels were added to the issue and @aaron0browne was assigned as well.

## Template Format

A sample template file is included [here](ghform/rfc.json). Template files are in json format, with the following structure (where `...` represents a repeating structure in a list):

```json
{
    "name": "Form Name",
    "fields": [
        {
            "name": "top level field name",
            "type": "field type",
            "description": "field description"
        },
        ...
    ],
    "groups": [
        {
            "name": "Group Name",
            "fields": [
                {
                    "name": "group level field name",
                    "type": "field type",
                    "description": "field description"
                },
                ...
            ]
            
        },
        ...
    ]
}
```

## Field Types and Attributes

The defined field types are:

- `text`
- `url/text`
- `datetime`
- `time`
- `choice`
- `username`

Additionally, fields may have the following attributes:

- `options`
- `default`
- `action`

### Text

These fields perform no validation and the response is inserted on the line below the field name when output.

### URL/Text

In addition to being inserted below the field name on output, if the response to these fields is a single string without any whitespace, it is assumed to be a a URL and deemed invalid if it can't be opened. Additionally, if the URL ends with `.png`, `.jpg`, `.gif`, `.psd`, or `.svg`, the image is included inline in the output.

### Datetime

These fields are validated against a `MM-DD-YY HH:MM` format and output directly to the right of the field name.

### Time

These fields are validated againast a `HH:MM` format and output directly to the right of the field name.

### Choice

These fields include the `options` attribute in the template and responses are validated against the option list. Responses are output directly to the right of the field name.

### Username

These fields are validated against the GitHub user database. If they include an `options` attribute, responses are additionally validated againast the option list. Output is to the right of the field name.

### Options

This attribute should be a list of objects, with each object containing a name and optionally a label (example below). If a label is included and that option is chosen, the label is applied to the pull request. Options are shown when user responses are gathered at the command line.

```json
"options": [
    {
        "name": "option name",
        "label": "optional label to be applied if chosen"
    },
    ...
]
```

### Default

Any field type may define a default (a string), which is suggested when responses are gathered. If the default is not defined for a field with options, the first option is used. On a username field, if the default is `submitter`, the pull request submitter is used. If a form of the given template has already been created on the given pull request, the existing response is used as the default for all fields.

### Action

The only currently defined action is `assign` on username fields. The chosen user will be assigned to the pull request.

## Further Development

- Fix `rfc` label bug where the label gets added and immediately removed
- Ability to define standard 'plans' as URLs on a per target repo basis

Please open an issue if you have a suggestion or find a bug.
