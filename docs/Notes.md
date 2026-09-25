Wargaming Design Lexicon

A structured terminology database for miniature and tabletop wargame design.

The short version: this repository contains a large, researched collection of wargaming mechanics, terminology, mechanical patterns, aliases and design concepts gathered from publicly accessible rules, official glossaries, quick-reference sheets, SRDs, publisher resources and other legitimate sources.

It is intended as a design reference, not a collection of copied rules.

The database currently contains 1,896 canonical terms.

Each entry attempts to answer a useful question:

What do we call this thing?

Sometimes a mechanic has an established name. Sometimes six games have six names for approximately the same idea. Sometimes a rule contains an interesting mechanical relationship that deserves a useful generic name of its own.

That is what this project is trying to map.

Files

The two important files are:

wargaming_design_lexicon_master_v68.xlsx wargaming_design_lexicon_v68.csv 

They contain substantially the same core lexicon, but they have different jobs.

XLSX

The Excel workbook is the research master.

Keep it.

It contains the main Lexicon plus source information, research batches, metadata and the working structure used when expanding the project.

If you want to continue researching and adding terminology, work from the latest .xlsx file.

CSV

The CSV is the machine-friendly database export.

Use this for:

websites

JavaScript

Python

search tools

database imports

data analysis

static site generators

GitHub-based applications

experiments you will inevitably forget about six months later

If you only want to build software using the lexicon, you probably want the CSV.

Idiot's Guide

This section assumes you have never used a CSV as a database, have only a vague idea what Git is doing, and would rather be designing tiny tanks than debugging data pipelines.

Fair enough.

1. Download the repository

The easiest method requires no Git knowledge at all.

On GitHub:

Open the repository.

Click Code.

Click Download ZIP.

Extract the ZIP somewhere sensible.

You now have the database.

Nothing needs installing just to read it.

2. Open the database

If you have Microsoft Excel

Open:

wargaming_design_lexicon_master_v68.xlsx 

If you use LibreOffice

Open the same .xlsx file in LibreOffice Calc.

If you use Google Sheets

Create a spreadsheet and import the .xlsx or .csv file.

If you are writing software

Use:

wargaming_design_lexicon_v68.csv 

That is the simpler file to consume programmatically.

What is actually in a record?

The lexicon is deliberately more than a giant list of words.

A typical record contains fields such as:

ID Term Aliases Category Mechanic / Type Definition Mechanical Role Typical Value / Unit Designer Note Game / Source Family Generic vs Specific Source ID Source URL Version Search Tags 

The exact spreadsheet structure may expand as the project develops.

Do not write software that assumes nobody will ever add another column. Future-you will curse present-you, and present-you will deserve it.

The important fields

ID

Example:

WG-1896 

This is the stable identifier for a canonical lexicon entry.

Software should preferably reference the ID rather than relying entirely on the term name.

Names can change.

IDs should not.

Term

The canonical name used by the lexicon.

Example:

Reinforcement Line 

This may be an established rules term or a generic descriptive term created to represent a recurring design pattern.

Aliases

Alternative names, closely related terminology or the original system terminology where appropriate.

This is particularly useful for searching.

A designer might search for:

morale 

while another thinks in terms of:

nerve 

and somebody else calls essentially the same family of mechanics:

battle shock 

The aliases help connect those vocabularies.

They do not necessarily mean the mechanics are identical.

Category

The broad design area.

Examples might include:

Movement Combat Morale Command Activation Objectives Resources Army Building Damage Magic 

Categories are deliberately broad.

Use the more detailed fields when you need precision.

Mechanic / Type

This describes what the rule actually does.

For example:

Resource-overload loss of control 

is more mechanically informative than merely knowing that the rule came from a fantasy monster game.

Definition

A concise paraphrase of the concept.

These definitions are deliberately written as summaries rather than copied rules text.

The database is a terminology and design research project. It is not an excuse to assemble other people's rulebooks into one enormous spreadsheet.

Mechanical Role

This explains why the mechanism exists or what it contributes to play.

That distinction matters.

Consider:

Unit receives Stress. 

That tells you what happened.

Something like:

Converts repeated activation into accumulating tempo debt. 

tells you what the mechanism is doing to the game.

The latter is generally more useful to a designer.

Typical Value / Unit

This records the sort of measurement associated with the mechanic.

Examples:

inches D6 D10 tokens cards models points percentage integer resource points 

It is not necessarily a prescribed value.

It is a clue to the mechanic's implementation.

Designer Note

This is the interpretative layer.

It records why a mechanic may be interesting, how it differs from superficially similar systems, or where the pattern might be reused.

These are design observations, not rules quotations.

Game / Source Family

This records where the terminology or mechanical inspiration came from.

A term may originate with a particular game while representing a much broader design idea.

Which leads us neatly to...

Generic vs Specific

This is important.

The database deliberately distinguishes between:

Generic concepts

Mechanics that make sense independently of the game where they were found.

For example:

Carried-Objective Movement Cap 

is useful terminology even if your game contains neither Moonstones nor goblins.

System-specific terminology

Names that have particular significance within one game's rules language.

For example, a named state, resource or action may be worth documenting because designers encounter it when researching that system.

System-specific implementations of generic concepts

This is the interesting middle ground.

A game may have a distinctive implementation of a broader design pattern.

The database attempts to preserve both pieces of information instead of flattening everything into vague synonyms.

Sources

The workbook contains a dedicated source register.

Sources may include:

official rulebooks

publisher PDFs

official rules wikis

quick-reference sheets

SRDs

official FAQs

errata

living rules

legitimate free rules

publisher design articles

Where practical, records include a source identifier and URL.

The purpose is provenance.

You should be able to determine why an entry exists and where its underlying concept came from.

What this database is NOT

It is not a pirate rulebook archive.

It does not attempt to reproduce complete copyrighted rules.

It does not assume that two mechanics are identical merely because publishers gave them similar names.

It is also not claiming that every term in tabletop wargaming has now been discovered.

That would be optimistic bordering on deranged.

The project is a growing research lexicon.

Searching the database

The simplest method is just searching the spreadsheet.

Try terms such as:

suppression activation initiative reaction command morale objective reserve damage cover 

But the real value comes from searching across several columns.

If you are designing a morale system, don't search only for:

Morale 

Try:

panic stress suppression rout break nerve cohesion shock withdrawal flee 

Different games solve similar problems using very different vocabulary.

That linguistic mess is one of the reasons this database exists.

Using the CSV in Python

You do not need a database server.

Python can read the CSV directly.

import csv with open( "wargaming_design_lexicon_v68.csv", encoding="utf-8-sig" ) as file: reader = csv.DictReader(file) for row in reader: print(row["Term"]) 

For more serious analysis, Pandas is convenient:

import pandas as pd lexicon = pd.read_csv( "wargaming_design_lexicon_v68.csv" ) print(lexicon.head()) 

Search for a word:

results = lexicon[ lexicon["Term"].str.contains( "morale", case=False, na=False ) ] print(results) 

Using the CSV in JavaScript

For a website, a CSV parser such as Papa Parse can load the file.

Conceptually:

Papa.parse("wargaming_design_lexicon_v68.csv", { download: true, header: true, complete: function(results) { console.log(results.data); } }); 

For a small static reference site, that may genuinely be all you need.

Do not deploy PostgreSQL because you have 1,896 rows and recently watched a database tutorial.

Using SQLite

If the project grows into a proper application, SQLite is a sensible next step.

You might create a table resembling:

CREATE TABLE lexicon ( id TEXT PRIMARY KEY, term TEXT, aliases TEXT, category TEXT, mechanic_type TEXT, definition TEXT, mechanical_role TEXT, typical_value_unit TEXT, designer_note TEXT, source_family TEXT, classification TEXT, source_id TEXT, source_url TEXT, version TEXT, search_tags TEXT ); 

Then import the CSV.

SQLite gives you fast searching and filtering without requiring a database server.

For this project's current scale, it is more than capable.

Suggested repository structure

A clean repository might look like:

wargaming-design-lexicon/ │ ├── README.md ├── DESCRIPTION.md ├── LICENSE │ ├── data/ │ ├── wargaming_design_lexicon.csv │ └── wargaming_design_lexicon_master.xlsx │ ├── archive/ │ ├── v67/ │ ├── v66/ │ └── ... │ ├── docs/ │ └── methodology.md │ └── examples/ ├── python-search.py └── javascript-search.html 

You do not need to retain every historical version in the root directory.

That gets messy surprisingly quickly.

Put old releases in /archive, use Git history, or create GitHub releases.

Updating the database

The working process is:

Public rules research ↓ Candidate terminology ↓ Compare against existing lexicon ↓ Reject duplicates ↓ Paraphrase the mechanic ↓ Classify generic/system-specific ↓ Record provenance ↓ Append to XLSX master ↓ Export canonical CSV ↓ Commit to GitHub 

The XLSX is the research master.

The CSV is the application/database export.

Do not independently edit both if you can avoid it.

Otherwise they will eventually disagree.

Recommended update procedure

When adding another research batch:

Start with the newest master XLSX.

Research new public and legitimate rules sources.

Search existing terminology before adding anything.

Reject exact duplicates.

Check near-duplicates manually.

Add genuinely distinct concepts.

Record source provenance.

Give each canonical term a new WG-#### identifier.

Update the version.

Export a fresh CSV.

Replace the current files in /data.

Commit both files together.

Example commit:

Update lexicon to v68 

Or, if you want slightly more information:

v68: add Conquest activation and reinforcement terminology 

Versioning

Research batches currently use simple incremental versions:

v66 v67 v68 

Canonical IDs are independent:

WG-0001 WG-0002 ... WG-1896 

Do not recycle IDs when deleting or merging entries.

A retired identifier is less dangerous than an identifier that suddenly means something different.

Adding terminology manually

Before adding a term, ask:

Does this already exist under another name?

Is the mechanic actually different?

Is this useful to a game designer?

Can it be described without copying copyrighted rules text?

Do we know where it came from?

Is it generic, system-specific, or both?

What mechanical problem does it solve?

If you cannot answer those questions, the entry probably needs more research.

De-duplication

This is increasingly important.

With nearly two thousand terms, exact duplicates are the easy problem.

Semantic duplicates are harder.

For example:

Retreat Fall Back Withdraw Disengage Break Contact 

might represent five different mechanics.

Or they might represent five publishers naming nearly the same mechanic differently.

Do not merge terms purely because the English sounds similar.

Compare:

trigger

timing

cost

target

movement

restrictions

consequences

persistence

interaction with other systems

If those differ meaningfully, separate entries may be justified.

Adding a new game

When researching a game, useful source priority is roughly:

Current official rules ↓ Official living rules / rules wiki ↓ Official FAQ and errata ↓ Official quick-reference material ↓ Official older editions ↓ Legally distributed third-party references 

Community material can help locate terminology, but wherever possible the actual database provenance should lead back to an authoritative source.

Research rule

Extract:

terminology

aliases

concise meanings

mechanical relationships

units and values

design roles

provenance

Do not extract long passages of rules text.

The objective is to understand mechanisms, not reproduce books.

A useful way to think about the project

Imagine that you are designing a rule and thinking:

I want units to activate repeatedly, but repeated activation should gradually make them unreliable.

You can search the lexicon and discover mechanisms such as stress accumulation, resource debt, exhaustion, action penalties or forced behaviour.

You are not looking for a rule to copy.

You are looking for the design vocabulary around the problem.

That distinction is the entire point.

Current status

Current database version:

v68 

Canonical terminology records:

1,896 

Latest canonical ID:

WG-1896 

The database spans historical, fantasy, science-fiction, naval, aerial, skirmish, mass-battle and other miniature-game design traditions.

It is still growing.

Quite substantially, judging by the spreadsheet.

Licence

See the repository LICENSE file for the project's licence.

Source game names, trademarks and referenced rules remain the property of their respective owners.

Database entries should remain concise, transformative descriptions of terminology and mechanical concepts rather than reproductions of source rules.

Contributing

Contributions are useful, but provenance matters more than volume.

A good contribution includes:

the proposed term

aliases

concise paraphrased definition

mechanical role

game/source

source URL

generic/system-specific classification

explanation of why it is not already represented

Ten well-researched additions are considerably more useful than 500 mechanically identical synonyms dumped into the CSV.

Final check

If you just want to look things up:

Open the XLSX. 

If you want to build a website or program:

Use the CSV. (I will at some point.)

If you want to add researched terminology:

Update the XLSX first. Export a new CSV afterwards. 

If you have somehow reached this point and are still editing both independently:

Stop doing that. it's enough..

One master. One generated export. Much less swearing.

