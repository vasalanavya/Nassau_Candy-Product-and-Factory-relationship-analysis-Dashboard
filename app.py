import streamlit as st
import pandas as pd
import plotly.express as px
# ==========================================
# MODULE: PRODUCT AND FACTORY ANALYSIS
# NASSAU CANDY DISTRIBUTOR PROJECT
# ==========================================
st.header("Product and Factory Relationship Analysis")

st.write(
    "This module analyses the relationship between "
    "products, divisions and factories."
)

# Use the existing main dataset: df
# Expected columns:
# Product Name, Division, Sales, Cost,
# Gross Profit, Units

required_columns = [
    "Product Name",
    "Division",
    "Sales",
    "Cost",
    "Gross Profit",
    "Units"
]
# Load Factory Mapping CSV
factory_df = pd.read_csv(
    "/content/Nassau Candy Distributor.csv"
)

# Clean column names
factory_df.columns = (
    factory_df.columns.astype(str).str.strip()
)

# Display available columns
print("Factory Mapping Columns:")
print(factory_df.columns.tolist())
# Check required columns
required_columns = ["Product Name", "Division"]

missing_columns = [
    col for col in required_columns
    if col not in factory_df.columns
]

if missing_columns:
    st.error(
        f"Missing columns in Factory Mapping: {missing_columns}"
    )
    st.stop()

else:
    # Make a separate copy
    factory_df = factory_df.copy()

    # Clean Product Name
    factory_df["Product Name"] = (
        factory_df["Product Name"]
        .astype("string")
        .str.strip()
    )

    # Clean Division
    factory_df["Division"] = (
        factory_df["Division"]
        .astype("string")
        .str.strip()
    )


    # Clean product and division names
    factory_df["Product Name"] = (
        factory_df["Product Name"].astype("string").str.strip()
    )

    factory_df["Division"] = (
        factory_df["Division"].astype("string").str.strip()
    )

    # Numeric conversion
    numeric_columns = [
        "Sales", "Cost", "Gross Profit", "Units"
    ]

    for col in numeric_columns:
        factory_df[col] = pd.to_numeric(
            factory_df[col], errors="coerce"
        )

    # ======================================
    # FACTORY MAPPING
    # ======================================

    if "Factory" not in factory_df.columns:

        st.info(
            "Factory column is not available in the "
            "original dataset. Upload a separate "
            "Product Name and Factory mapping CSV."
        )

        uploaded_mapping = st.file_uploader(
            "Upload Factory_Mapping.csv",
            type=["csv"],
            key="factory_mapping"
        )

        if uploaded_mapping is not None:

            mapping_df = pd.read_csv(uploaded_mapping)

            mapping_df.columns = (
                mapping_df.columns.astype(str).str.strip()
            )

            if {"Product Name", "Factory"}.issubset(
                mapping_df.columns
            ):

                mapping_df["Product Name"] = (
                    mapping_df["Product Name"]
                    .astype("string").str.strip()
                )

                mapping_df["Factory"] = (
                    mapping_df["Factory"]
                    .astype("string").str.strip()
                )

                # Avoid duplicate product mappings
                mapping_df = mapping_df.drop_duplicates(
                    subset=["Product Name"]
                )

                factory_df = factory_df.merge(
                    mapping_df[["Product Name", "Factory"]],
                    on="Product Name",
                    how="left"
                )

            else:
                st.error(
                    "Mapping CSV must contain Product Name "
                    "and Factory columns."
                )

    # ======================================
    # CHECK FACTORY INFORMATION
    # ======================================

    if "Factory" not in factory_df.columns:

        st.warning(
            "Please upload the factory mapping CSV "
            "to view factory analysis."
        )

    elif factory_df["Factory"].notna().sum() == 0:

        st.warning(
            "No matching factory information found. "
            "Check the product names in your mapping file."
        )

    else:

        factory_df["Factory"] = (
            factory_df["Factory"].astype("string").str.strip()
        )

        factory_df = factory_df.dropna(
            subset=["Factory"]
        )

        factory_df = factory_df[
            factory_df["Factory"] != ""
        ]

        # ==================================
        # KPI CALCULATIONS
        # ==================================

        total_factories = factory_df["Factory"].nunique()

        total_products = factory_df["Product Name"].nunique()

        total_sales = factory_df["Sales"].sum()

        total_profit = factory_df["Gross Profit"].sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Factories", total_factories)

        col2.metric("Total Products", total_products)

        col3.metric("Factory-associated Sales",
                    f"{total_sales:,.2f}")

        col4.metric("Factory-associated Gross Profit",
                    f"{total_profit:,.2f}")

        st.divider()

        # ==================================
        # 1. FACTORY-WISE PRODUCT COUNT
        # ==================================

        st.subheader("1. Factory-wise Product Distribution")

        factory_products = (
            factory_df.groupby("Factory")["Product Name"]
            .nunique()
            .reset_index(name="Product Count")
            .sort_values("Product Count", ascending=False)
        )

        fig1 = px.bar(
            factory_products,
            x="Factory",
            y="Product Count",
            color="Factory",
            title="Number of Products Associated with Each Factory"
        )

        st.plotly_chart(fig1, use_container_width=True)

        st.dataframe(
            factory_products,
            use_container_width=True
        )

        # ==================================
        # 2. DIVISION-WISE PRODUCT COUNT
        # ==================================

        st.subheader("2. Division-wise Product Distribution")

        division_products = (
            factory_df.groupby("Division")["Product Name"]
            .nunique()
            .reset_index(name="Product Count")
        )

        fig2 = px.bar(
            division_products,
            x="Division",
            y="Product Count",
            color="Division",
            title="Products Available in Each Division"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # ==================================
        # 3. DIVISION VS FACTORY
        # ==================================

        st.subheader("3. Division and Factory Relationship")

        division_factory = (
            factory_df.groupby(
                ["Division", "Factory"]
            )["Product Name"]
            .nunique()
            .reset_index(name="Product Count")
        )

        fig3 = px.bar(
            division_factory,
            x="Division",
            y="Product Count",
            color="Factory",
            barmode="group",
            title="Product Distribution by Division and Factory"
        )

        st.plotly_chart(fig3, use_container_width=True)

        # ==================================
        # 4. FACTORY-WISE SALES
        # ==================================

        st.subheader("4. Factory-wise Sales Performance")

        factory_sales = (
            factory_df.groupby("Factory", as_index=False)
            ["Sales"].sum()
        )

        fig4 = px.bar(
            factory_sales,
            x="Factory",
            y="Sales",
            color="Factory",
            title="Sales Associated with Each Factory"
        )

        st.plotly_chart(fig4, use_container_width=True)

        # ==================================
        # 5. FACTORY-WISE GROSS PROFIT
        # ==================================

        st.subheader("5. Factory-wise Gross Profit")

        factory_profit = (
            factory_df.groupby("Factory", as_index=False)
            ["Gross Profit"].sum()
        )

        fig5 = px.bar(
            factory_profit,
            x="Factory",
            y="Gross Profit",
            color="Factory",
            title="Gross Profit Associated with Each Factory"
        )

        st.plotly_chart(fig5, use_container_width=True)

        # ==================================
        # 6. FACTORY-WISE PROFIT MARGIN
        # ==================================

        st.subheader("6. Factory-wise Gross Margin")

        factory_margin = (
            factory_df.groupby("Factory")
            .agg({
                "Sales": "sum",
                "Gross Profit": "sum"
            })
            .reset_index()
        )

        factory_margin["Gross Margin (%)"] = (
            factory_margin["Gross Profit"]
            .div(factory_margin["Sales"].replace(0, pd.NA))
            * 100
        )

        fig6 = px.bar(
            factory_margin,
            x="Factory",
            y="Gross Margin (%)",
            color="Factory",
            title="Gross Margin Percentage by Factory"
        )

        st.plotly_chart(fig6, use_container_width=True)

        # ==================================
        # 7. FACTORY SUMMARY TABLE
        # ==================================

        st.subheader("7. Factory Performance Summary")

        st.dataframe(
            factory_margin,
            use_container_width=True
        )

        st.success(
            "Product and Factory Analysis completed successfully!"
        )


