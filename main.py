import pathway as pw
from src.constraint_extractor import extract_constraints

class ChunkSchema(pw.Schema):
    chunk_id: int
    text: str

# 1. Read input text
chunks = pw.io.csv.read(
    "data/chunks.csv",
    schema=ChunkSchema,
    mode="static"
)

# 2. Wrap extractor as Pathway UDF
@pw.udf
def extract_constraints_udf(text: str, chunk_id: int):
    return extract_constraints(text, chunk_id)

# 3. Apply extraction
constraints_nested = chunks.select(
    constraints=extract_constraints_udf(chunks.text, chunks.chunk_id)
)

# 4. Flatten list → rows
constraints = constraints_nested.flatten(pw.this.constraints)

# 5. Write output
pw.io.jsonlines.write(constraints, "output/constraints.jsonl")

constraints.debug("DEBUG_CONSTRAINTS")


# 6. Run pipeline
pw.run()
