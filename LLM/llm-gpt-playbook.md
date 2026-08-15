# LLM
Large Language Models (LLMs) - A type of foundation model that is designed to understand and generate human language. LLMs are trained on massive datasets of text and code, and they can be used for many tasks, such as writing, translating, and coding.

##  how LLM tokens work?

### Tokenizer

Tokens are the CURRENCY of LLMs. LLM cost is charged by Tokens.
![alt text](image-3.png)

Every model have different inputtokens and output tokens for same words and price per 1k tokens is also different.
![alt text](image-4.png)

Now, come to concept of Encoding and Decoding

### Encoding
Turning "Text" into "Tokens".

![alt text](image-5.png)

End-to-End Process - LLM are Large Language Model but they do not understand Language. LLM is not dealing with "words", it deals with Tokens (Numbers) / Vectors.

![alt text](image-6.png)

![alt text](image-7.png)

### Decoding
![alt text](image-8.png)

### Tokenizer training
![alt text](image-9.png)

![alt text](image-10.png)


## Word Embedding / Vector Embedding / Embeddings
AI Turns "Words" into "Vectors". Vectors are numbers.

It turns word into special number call vector. 
![alt text](image.png)

![alt text](image-1.png)

### LLM Embeddings

![alt text](image-2.png)

![alt text](image-11.png)

![alt text](image-12.png)

![alt text](image-14.png)

![alt text](image-13.png)


# GPTs - Generative Pre-trained Transformer 
A type of AI model designed to understand and create human-like text, code and images.

![alt text](image-16.png)

![alt text](image-15.png)

## LLM Concepts

Weights, Context and Memory

#### Weights - Core parameters in LLM models learned during training and fine-tuning. These are basically languages, coding, maths, reasoing, everything LLM model learns. 

#### Context - Context containes input prompt + model response. Context is dynamic and changed with each interection.

#### Memory - Memory allows LLMs to retain infomation for long term beyong single interection and use across multiple interections. It persists across sessions.

![alt text](image-17.png)

#### Context Windows

Input + output tokens make context window.
![alt text](image-18.png)

Each model provider have setup limit for context window.

![alt text](image-19.png)

Why there is limit?
1. LLM processing is expensive, more tokens means more processing
2. Larger the context window, more performance degrade.

![alt text](image-20.png)

![alt text](image-21.png)

![alt text](image-22.png)


