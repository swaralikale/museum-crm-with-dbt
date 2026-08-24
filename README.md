# Museum CRM Analytics Pipeline with dbt

## Running Order

1. Create the project directory and move into it.

2. Start PostgreSQL in Docker and create the museum database.

3. Install dbt and Faker in a Python virtual environment.

4. Initialize the dbt project and confirm the database connection.

5. Write a Python data generator to create tables of realistic CRM data with seeded randomness.

6. Run the generator and verify both row counts and presence of dirty data.

7. Declare all raw tables as dbt sources with column-level documentation.

8. Create staging SQL models that clean and standardize each raw table.

9. Add data quality tests that enforce contracts on primary keys, statuses, and relationships.

10. Run dbt build and observe test failures caused by dirty source data.

11. Update staging models to handle null values, duplicates, and invalid statuses.

12. Re-run the full test suite and confirm all tests passed.

13. Create five analytics mart models covering member lifetime value, visitor conversion, donor segmentation, campaign performance, and ticket/coupon analysis.

14. Add a singular data test that detects duplicate contacts across the CRM.

15. Generate dbt documentation and view the full data lineage from raw sources through marts.

16. Configure source freshness with warn and error thresholds on all raw tables.

17. Write a custom generic test macro for email format validation using Jinja.

18. Apply the custom test to contact email columns and verify with dbt tags.

19. Add visit cadence per contact with a frequency segment across all contacts.

20. Add lifetime value ranking/quartiles for member segmentation.







All required scripts available in [data_generation](data_generation) and [dbt_project](dbt_project) folders. View the Lineage Graph [here](lineage_graph/graph_2.png).

**IMPORTANT NOTE:** Replace the password placeholder in [Generator Python file](data_generation/generate_museum_data.py) with your set password before running.


## References
[1] PostgreSQL Global Development Group, "PostgreSQL 16 Documentation," PostgreSQL [Online]. Available: https://postgresql.org .

[2] dbt Labs, "dbt-core," version 1.12.3, PyPI [Online]. Available: https://pypi.org/project/dbt-core/ . 

[3] A. Velasco, ‘Veevart’, Veevart. [Online]. Available: https://veevart.com/blog/the-complete-guide-to-crm-for-museums-and-cultural-institutions

[4] Museum Booster, ‘Museum Innovation Barometer 2021 by MUSEUM BOOSTER’, Culture Action Europe, Aug. 2021. [Online]. Available: https://cultureactioneurope.org/wp-content/uploads/2021/08/Museum-Innovation-Barometer-2021.pdf

[5] T. Cravello, ‘NextWork - Museum CRM Data Pipeline with dbt’, NextWork. [Online]. Available: https://nextwork.ai/projects/4dab90e4-08a2-4bcf-a763-ededb6d40bc5







With special thanks to Tristan Cravello and the Nextwork team. 
