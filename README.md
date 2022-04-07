# legalAI
 Some useful modules for processing legal documents in Python

##### How to use

Refer to README.md in each module

##### **Package Requirements**

- `stanza` 1.2.3 or above

  The `common` module will start a Stanford CoreNLP server. This server will listen at port 9010.

  - The server requires Java Running Environment (JRE).

- `nltk` 3.6.5 or above

## Sentence Simplification

Split a compound or complex sentence into simple ones.

#### **API Functions:**

##### **`split_sentence`**

Split the sentence based on two gates.

| Argument     | Type    | Usage                                    | Remark           |
| ------------ | ------- | ---------------------------------------- | ---------------- |
| `sentence`   | string  | The sentence to be spliced               |                  |
| [`complex`]  | boolean | If recursively split a complex sentence  | By default, True |
| [`compound`] | boolean | If recursively split a compound sentence | By default, True |

**Return:**

A list of simple sentences

**Remarks:**

- The resultant sentences will not have ending punctuations.
- Will consider proper names. For example, the sentence "I ate Fish and Chip." will not be splitted, because "Fish and Chip" can be intelligently identified as proper names.

## Legal Concept Tree

#### **API Functions:**

##### **`get_concepts`**

Get the indexed tree data structure of legal concepts.

**Return:**

A map of tree nodes, where keys are legal terms and values are corresponding tree node.

**Definition of node:**

```python
class Node:
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        if parent:
            self.level = parent.level + 1
        else:
            self.level = 0
```

