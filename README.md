# legalAI
 Some useful modules for processing legal documents in Python

> #### Modules:
>
> `split_sentence`
>
> `concepts`
>
> #### How to use
>
> Copy the needed Python file to your project. Also copy the `./common` directory and put them on the same level.
>
> **Package Requirements**
>
> - `stanza` 1.2.3 or above
>
>   The `common` module requires the Stanford Dependency Parsing tool. This server will listen at port 9010.
>
> - `nltk` 3.6.5 or above

#### Sentence Simplification

Split a compound or complex sentence into simple ones.

##### **API Functions:**

**`split_sentence`**

Split the sentence based on two gates.

| Argument   | Type    | Usage                                  | Remark           |
| ---------- | ------- | -------------------------------------- | ---------------- |
| `sentence` | string  | The sentence to be spliced             |                  |
| `complex`  | boolean | If recursively split if it is complex  | By default, True |
| `compound` | boolean | If recursively split if it is compound | By default, True |

**Return:**

A list of simple sentences

**Remarks:**

- The resultant sentences will not have ending punctuations.
- Will consider proper names. For example, if the sentence is "I ate Fish and Chip.", it will not split the sentence.

#### Legal Concept Tree

Get the nice tree data structure of legal concepts.





 

