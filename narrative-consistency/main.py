import pathway as pw
from src.constraint_extractor import extract_constraints

class ChunkSchema(pw.Schema):
    chunk_id: int
    book_name: str
    text: str

# 1. Read input text
chunks = pw.io.csv.read(
    "data/chunks_sampled.csv",
    schema=ChunkSchema,
    mode="static"
)

# 2. Wrap extractor as Pathway UDF
@pw.udf
def extract_constraints_udf(text: str, chunk_id: int, book_name: str):
    return extract_constraints(text, chunk_id, book_name)

# 3. Apply extraction
constraints_nested = chunks.select(
    constraints=extract_constraints_udf(chunks.text, chunks.chunk_id, chunks.book_name)
)

# 4. Flatten list → rows
constraints = constraints_nested.flatten(pw.this.constraints)

# 5. Write output
pw.io.jsonlines.write(constraints, "output/constraints.jsonl")

# 6. Run pipeline
pw.run()
