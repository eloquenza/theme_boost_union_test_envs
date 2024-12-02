from enum import Enum


class MoodlePlugin(str, Enum):
    def __str__(self) -> str:
        return str(self.value)

    ATTO_STYLES = "atto_styles"
    AVAILABILITY_COHORT = "availability_cohort"
    AVAILABILITY_PASSWORD = "availability_password"
    AVAILABILITY_ROLE = "availability_role"
    AUTH_LDAP_SYNCPLUS = "auth_ldap_syncplus"
    BLOCK_COHORTSPECIFICHTML = "block_cohortspecifichtml"
    BLOCK_PEOPLE = "block_people"
    BOOKIT = "bookit"
    BOOST_UNION = "boost_union"
    BOOST_UNION_CHILD = "boost_union_child"
    LOCAL_BULKENROL = "local_bulkenrol"
    LOCAL_MAINTENANCE_LIVECHECK = "local_maintenance_livecheck"
    LOCAL_NAVBARPLUS = "local_navbarplus"
    LOCAL_PROFILECOHORT = "local_profilecohort"
    LOCAL_PROFILETHEME = "local_profiletheme"
    LOCAL_RESORT_COURSES = "local_resort_courses"
    LOCAL_SANDBOX = "local_sandbox"
    LOCAL_SESSION_KEEPALIVE = "local_session_keepalive"
    LOCAL_STATICPAGE = "local_staticpage"
    TOOL_COURSEFIELDS = "tool_coursefields"
