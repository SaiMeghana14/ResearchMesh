import streamlit as st
from datetime import datetime, timedelta

CONSENT_VALIDITY_HOURS = 24  # consents expire after 24h


class GovernanceAgent:
    def __init__(self, ledger):
        self.ledger = ledger
        if "consents" not in st.session_state:
            st.session_state["consents"] = []  # replay memory

    def display(self):
        st.subheader("🛡 Governance Agent")

        user = st.text_input("Enter requesting user:")
        dataset = st.text_input("Dataset name:")

        # Access type choice
        access_type = st.radio(
            "Requested Access Type",
            ["Raw Data", "Anonymized Data", "Aggregated Results"],
            index=0,
        )

        if st.button("Request Consent"):
            if not user or not dataset:
                st.warning("Please enter both user and dataset.")
                return

            now = datetime.utcnow()

            # Check replay memory
            for c in st.session_state["consents"]:
                if (
                    c["user"] == user
                    and c["dataset"] == dataset
                    and c["access_type"] == access_type
                ):
                    expiry = c["expiry"]
                    if now < expiry:
                        st.info(
                            f"⚡ Consent already granted earlier for {user} "
                            f"on {dataset} ({access_type}).\n"
                            f"✅ Valid until {expiry.strftime('%Y-%m-%d %H:%M:%S UTC')}."
                        )
                        return
                    else:
                        st.warning(
                            f"⏳ Previous consent for {dataset} ({access_type}) expired "
                            f"at {expiry.strftime('%Y-%m-%d %H:%M:%S UTC')}."
                        )
                        break  # allow new consent grant

            # Cross-agent style negotiation demo
            if access_type == "Raw Data" and user.lower().startswith("external"):
                st.warning(
                    f"❌ Raw data access denied for external user {user}. "
                    f"🔄 Offering anonymized data instead."
                )
                access_type = "Anonymized Data"

            # Grant new consent
            expiry_time = now + timedelta(hours=CONSENT_VALIDITY_HOURS)
            consent_record = {
                "user": user,
                "dataset": dataset,
                "access_type": access_type,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "expiry": expiry_time,
            }
            st.session_state["consents"].append(consent_record)

            st.success(
                f"✅ Consent granted to {user} for {access_type} on {dataset}.\n"
                f"📅 Valid until {expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}."
            )
            self.ledger.log(
                actor=user,
                action=f"CONSENT_GRANTED_{access_type.upper().replace(' ', '_')}",
                resource=dataset,
            )

        if st.checkbox("Show Consent Replay Memory"):
            if st.session_state["consents"]:
                st.table(
                    [
                        {
                            "User": c["user"],
                            "Dataset": c["dataset"],
                            "Access Type": c["access_type"],
                            "Granted At": c["timestamp"],
                            "Valid Until": c["expiry"].strftime(
                                "%Y-%m-%d %H:%M:%S UTC"
                            ),
                        }
                        for c in st.session_state["consents"]
                    ]
                )
            else:
                st.info("No past consents stored.")
