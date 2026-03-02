import time
import json
from datetime import datetime
from knowledgelm.core.forum import ReferenceExtractor

def create_synthetic_data(num_posts=500, links_per_post=2):
    posts = []
    links = []

    for i in range(1, num_posts + 1):
        # Create a post
        post = {
            "id": i + 10000,
            "post_number": i,
            "created_at": f"2023-01-{i%28 + 1:02d}T10:00:00Z",
            "cooked": f"<p>This is post {i} content.</p>"
        }
        posts.append(post)

        # Create links for this post
        for j in range(links_per_post):
            link = {
                "url": f"https://example.com/link_{i}_{j}",
                "title": f"Example Link {i}-{j}",
                "clicks": i % 5,
                "post_number": i,
                "internal": False,
                "reflection": False
            }
            links.append(link)

    thread_data = {
        "title": "Synthetic Benchmark Thread",
        "slug": "synthetic-benchmark",
        "id": 12345,
        "details": {
            "links": links
        },
        "posts": posts
    }

    return thread_data

def run_benchmark(iterations=100):
    thread_data = create_synthetic_data(num_posts=500, links_per_post=2)
    extractor = ReferenceExtractor()

    # Warmup
    extractor.extract_references(thread_data)

    start_time = time.perf_counter()
    for _ in range(iterations):
        extractor.extract_references(thread_data)
    end_time = time.perf_counter()

    avg_time_ms = ((end_time - start_time) / iterations) * 1000
    print(f"Average execution time over {iterations} iterations: {avg_time_ms:.4f} ms")
    return avg_time_ms

if __name__ == "__main__":
    print("Running benchmark...")
    run_benchmark(iterations=1000)
