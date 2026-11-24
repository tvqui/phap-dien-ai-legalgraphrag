# Graph ON / OFF: mở rộng Graph theo chỗ thiếu

Nhãn DRAFT; tập phát triển đã sử dụng trước đây. CI là bootstrap theo câu hỏi; không phải chứng nhận đúng luật.

| Nhóm | Chỉ số | Câu ghép / dự kiến | OFF | ON | ON − OFF | CI 95% |
|---|---|---:|---:|---:|---:|---|
| all | ai_correctness | 47/47 | 0.9362 | 0.9468 | 0.0106 | [-0.0319, 0.0638] |
| all | ai_completeness | 47/47 | 0.9340 | 0.9213 | -0.0128 | [-0.0383, 0.0000] |
| all | ai_evidence_support | 47/47 | 0.9362 | 0.9149 | -0.0213 | [-0.0638, 0.0000] |
| all | gold_citation_group_recall | 47/47 | 0.6383 | 0.6383 | 0.0000 | [0.0000, 0.0000] |
| all | citation_locator_metadata_match | 33/47 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| all | citation_url_metadata_match | 33/47 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| all | elapsed_ms | 47/47 | 31125.6262 | 29328.3440 | -1797.2822 | [-3990.5865, 948.2100] |
| behavioral_controls | ai_correctness | 12/12 | 1.0000 | 0.9583 | -0.0417 | [-0.1250, 0.0000] |
| behavioral_controls | ai_completeness | 12/12 | 0.9917 | 0.9417 | -0.0500 | [-0.1500, 0.0000] |
| behavioral_controls | ai_evidence_support | 12/12 | 1.0000 | 0.9167 | -0.0833 | [-0.2500, 0.0000] |
| behavioral_controls | gold_citation_group_recall | 12/12 | 0.0833 | 0.0833 | 0.0000 | [0.0000, 0.0000] |
| behavioral_controls | citation_locator_metadata_match | 1/12 | 1.0000 | 1.0000 | 0.0000 | [N/A, N/A] |
| behavioral_controls | citation_url_metadata_match | 1/12 | 1.0000 | 1.0000 | 0.0000 | [N/A, N/A] |
| behavioral_controls | elapsed_ms | 12/12 | 7052.4556 | 5688.4325 | -1364.0230 | [-4093.0600, 1.9533] |
| conditions_hypothesis | ai_correctness | 16/16 | 0.9375 | 0.9375 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | ai_completeness | 16/16 | 0.9375 | 0.9375 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | ai_evidence_support | 16/16 | 0.9375 | 0.9375 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | gold_citation_group_recall | 16/16 | 0.8438 | 0.8438 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | citation_locator_metadata_match | 15/16 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | citation_url_metadata_match | 15/16 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| conditions_hypothesis | elapsed_ms | 16/16 | 39803.6349 | 38682.6070 | -1121.0279 | [-6736.4223, 6896.8464] |
| relationship_hypothesis | ai_correctness | 7/7 | 0.8571 | 0.8571 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | ai_completeness | 7/7 | 0.8571 | 0.8571 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | ai_evidence_support | 7/7 | 0.8571 | 0.8571 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | gold_citation_group_recall | 7/7 | 0.6429 | 0.6429 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | citation_locator_metadata_match | 6/7 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | citation_url_metadata_match | 6/7 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| relationship_hypothesis | elapsed_ms | 7/7 | 44823.0669 | 41833.9759 | -2989.0910 | [-5551.3600, -788.5463] |
| single_provision_controls | ai_correctness | 12/12 | 0.9167 | 1.0000 | 0.0833 | [0.0000, 0.2500] |
| single_provision_controls | ai_completeness | 12/12 | 0.9167 | 0.9167 | 0.0000 | [0.0000, 0.0000] |
| single_provision_controls | ai_evidence_support | 12/12 | 0.9167 | 0.9167 | 0.0000 | [0.0000, 0.0000] |
| single_provision_controls | gold_citation_group_recall | 12/12 | 0.9167 | 0.9167 | 0.0000 | [0.0000, 0.0000] |
| single_provision_controls | citation_locator_metadata_match | 11/12 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| single_provision_controls | citation_url_metadata_match | 11/12 | 1.0000 | 1.0000 | 0.0000 | [0.0000, 0.0000] |
| single_provision_controls | elapsed_ms | 12/12 | 35637.9448 | 33200.9528 | -2436.9920 | [-4940.5684, -475.9190] |
