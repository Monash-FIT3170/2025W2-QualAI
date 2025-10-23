class QDrantTemplates:
    @staticmethod
    def default_template(prompt: str, prompt_context: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert AI research assistant designed for qualitative analysis of interview transcripts. Your responses must be objective, precise, and strictly grounded in the provided context.
            </ROLE>
            <PROCESS>
                <STEP_1>Analyze the user's question to determine its nature.</STEP_1>
                <STEP_2>
                    If the question is conversational (e.g., greetings, pleasantries), provide a brief, polite response. Do not consult the context.
                </STEP_2>
                <STEP_3>
                    If the question is a research query, perform a detailed analysis of the <CONTEXT> to formulate your answer. Your answer must be synthesized directly from this information. Support your claims with direct quotes where appropriate.
                </STEP_3>
            </PROCESS>
            <RULES>
                <RULE id="1">NEVER use information outside of the provided <CONTEXT> block.</RULE>
                <RULE id="2" importance="CRITICAL">If the answer to a research query cannot be found in the <CONTEXT>, you must respond *only* with the phrase: "I could not find information on this topic in the provided transcript."</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <QUESTION>
                {prompt.strip()}
            </QUESTION>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <ANSWER>
        """

    @staticmethod
    def summary_template(prompt_context: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in creating concise summaries of qualitative data.
            </ROLE>
            <TASK>
                Create a brief, high-level summary of the key points in the provided context.
                Focus on the main themes, findings, and conclusions.
                Keep your summary concise (3-5 sentences maximum).
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Do not include detailed analysis or extensive quotes.</RULE>
                <RULE id="3">If the context is insufficient, state: "I could not find enough information to create a summary."</RULE>
                <RULE id="4">Respond only with the content for the <SUMMARY> section. Do not include any preface or reasoning.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <SUMMARY>
        """

    @staticmethod
    def summary_direct_template(target_text: str) -> str:
        """
        Summarise the provided text directly (no external context/RAG).
        """
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert at concise summaries.
            </ROLE>
            <TASK>
                Summarise the following text in 2-4 sentences, capturing the main point(s) without adding new facts.
            </TASK>
            <RULES>
                <RULE id="1">Base the summary ONLY on <TARGET_TEXT>.</RULE>
                <RULE id="2">Be clear, neutral, and concise.</RULE>
                <RULE id="3">Respond only with the content for the <SUMMARY> section. Do not include any preface or reasoning.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <TARGET_TEXT>
                {target_text.strip()}
            </TARGET_TEXT>
        </DATA>

        <SUMMARY>
        """

    @staticmethod
    def code_theme_template(prompt_context: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert qualitative researcher specializing in thematic analysis and coding.
            </ROLE>
            <TASK>
                Analyze the provided context to identify and extract key codes and themes.
                For each code/theme:
                1. Provide a clear label
                2. Include specific evidence from the text with direct quotes
                3. Note the frequency or prevalence of the theme
                4. Explain the significance of the theme

                Structure your response with clear headings for each theme.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Support each theme with at least one direct quote.</RULE>
                <RULE id="3">If no clear themes emerge, state: "I could not identify distinct themes in this content."</RULE>
                <RULE id="4">Respond only inside the <THEMATIC_ANALYSIS> section without preface.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <THEMATIC_ANALYSIS>
        """

    @staticmethod
    def outlier_template(prompt_context: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in identifying unusual or unexpected patterns in qualitative data.
            </ROLE>
            <TASK>
                Analyze the provided context to identify any outliers, anomalies, or unexpected findings.
                For each outlier:
                1. Clearly describe what makes it unusual
                2. Provide the specific evidence from the text
                3. Explain why it stands out from the rest of the content
                4. Suggest possible interpretations or implications

                Structure your response with clear headings for each outlier.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Support each outlier identification with specific evidence.</RULE>
                <RULE id="3">If no outliers are found, state: "I could not identify any significant outliers in this content."</RULE>
                <RULE id="4">Respond only inside the <OUTLIER_ANALYSIS> section without preface.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <OUTLIER_ANALYSIS>
        """

    @staticmethod
    def quote_template(prompt: str, prompt_context: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert research assistant specializing in finding and organizing relevant quotes from qualitative data.
            </ROLE>
            <TASK>
                Based on the user's query about a specific theme or topic, find all relevant quotes from the provided context.
                For each quote:
                1. Include the exact text from the context
                2. Note the speaker if available
                3. Provide a brief explanation of how it relates to the theme

                Organize the quotes by sub-themes or patterns that emerge.
            </TASK>
            <RULES>
                <RULE id="1">Only use information from the provided <CONTEXT>.</RULE>
                <RULE id="2">Include exact quotes, do not paraphrase.</RULE>
                <RULE id="3">If no relevant quotes are found, state: "I could not find quotes related to this theme in the provided content."</RULE>
                <RULE id="4">Respond only inside the <RELEVANT_QUOTES> section without preface.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <USER_QUERY>
                {prompt.strip()}
            </USER_QUERY>
            <CONTEXT>
                {prompt_context.strip()}
            </CONTEXT>
        </DATA>

        <RELEVANT_QUOTES>
        """

    @staticmethod
    def explain_template(target_text: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are an expert explainer.
            </ROLE>
            <TASK>
                Explain the following text clearly for a non-expert audience.
                Use plain language, short paragraphs, and brief bullet points if helpful.
                Do NOT add new facts beyond what the text provides.
            </TASK>
            <RULES>
                <RULE id="1">Base your explanation ONLY on <TARGET_TEXT>.</RULE>
                <RULE id="2">Avoid jargon unless you also define it simply.</RULE>
                <RULE id="3">Be concise and clear.</RULE>
                <RULE id="4">Respond only with the content for the <EXPLANATION> section. Do not include any preface or reasoning.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <TARGET_TEXT>
                {target_text.strip()}
            </TARGET_TEXT>
        </DATA>

        <EXPLANATION>
        """

    @staticmethod
    def rewrite_template(target_text: str) -> str:
        return f"""
        <INSTRUCTIONS>
            <ROLE>
                You are a precise editor.
            </ROLE>
            <TASK>
                Rewrite the following text to improve clarity and concision.
                Preserve the original meaning. Output only the rewritten text.
            </TASK>
            <RULES>
                <RULE id="1">Base your rewrite ONLY on <TARGET_TEXT>.</RULE>
                <RULE id="2">Keep tone neutral and professional unless tone is explicitly embedded in the text.</RULE>
                <RULE id="3">Remove filler, redundancy, and convoluted phrasing.</RULE>
                <RULE id="4">Respond only with the content for the <REWRITE> section. Do not include any preface or reasoning.</RULE>
            </RULES>
        </INSTRUCTIONS>

        <DATA>
            <TARGET_TEXT>
                {target_text.strip()}
            </TARGET_TEXT>
        </DATA>

        <REWRITE>
        """
