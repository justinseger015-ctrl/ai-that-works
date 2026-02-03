from baml_client import b
from baml_client.type_builder import TypeBuilder
from baml_client.types import Note

doctor_target = {
  "height": {
    "display_unit": "cm"
  }
}

def print_result(result: Note, schema: dict):
    print(f"Name: {result.name}")
    print("--------------------------------")
    for key, value_details in schema.items():
        value = getattr(result, key)
        if doctor_target.get(key, None) is not None:
            display_unit = doctor_target[key].get("display_unit", None)
        else:
            display_unit = None
        if value_details.type == "dropdown":
            value = value
        elif value_details.type == "bulleted_list":
            value = "\n- ".join(value) + "\n"
        elif value_details.type == "text":
            value = value
        elif value_details.type == "number":
            value = value
        else:
            raise ValueError(f"Invalid type: {value_details['type']}")
        display_unit_str = f" ({display_unit})" if display_unit is not None else ""
        print(f"{key}: {value} {display_unit_str}")

def main():
    schema = b.GenerateSchema("I care about the patient's temperature, age, height, weight, and some bulleted notes about their health.")
    print("Schema:")
    print(schema)
    print("--------------------------------")


    tb = TypeBuilder()
    note = tb.Note
    for key, value in schema.items():
        description = value.description
        if value.type == "dropdown":
            value_ty = tb.union([tb.literal_string(option) for option in value["options"]])
        elif value.type == "bulleted_list":
            value_ty = tb.list(tb.string())
            # true for all doctor targets
            description = "use short phrases; " + description
        elif value.type == "text":
            value_ty = tb.string()
        elif value.type == "number":
            value_ty = tb.int()
        property = note.add_property(key, value_ty)
        if description is not None:
            property.description(description)

    result = b.NotesFromTranscript(test_transcript, { "tb": tb })
    print_result(result, schema)




test_transcript = """
      Doctor: Good morning, Ms. Chen. I'm Dr. Walsh. I see you're here for your annual physical. How are you feeling today?
      Patient: Good morning, Doctor. I'm feeling well, thanks. Just here for the usual checkup.
      Doctor: Great. Let me pull up your chart—you're 42, is that right? And no significant medical history that I'm aware of?
      Patient: Yes, 42. Correct, no major issues. I had my tonsils out as a kid but nothing since.
      Doctor: Any current medications, supplements, or allergies we should have on file?
      Patient: No medications. I take a multivitamin and vitamin D. No allergies that I know of.
      Doctor: Good to know. Any changes in your health since last year—energy, sleep, appetite, weight?
      Patient: Nothing notable. I sleep pretty well, maybe six to seven hours. Appetite's normal. Weight's been stable.
      Doctor: Any chest pain, shortness of breath, dizziness, or palpitations?
      Patient: No, none of that.
      Doctor: Bowel and bladder habits normal? Any blood where it shouldn't be?
      Patient: All normal. No blood or anything unusual.
      Doctor: Stress level? Mood been okay?
      Patient: Work can be busy but I manage. Mood's been fine, no depression or anxiety to speak of.
      Doctor: Do you drink alcohol, smoke, or use any recreational drugs?
      Patient: I have a glass of wine with dinner sometimes. I've never smoked. No recreational drugs.
      Doctor: Any family history of heart disease, cancer, or diabetes we should keep an eye on?
      Patient: My father had high blood pressure. My mother's healthy. No cancer or diabetes in immediate family.
      Doctor: All right. I'll do a quick physical now—heart, lungs, abdomen, and a look at your skin. Then we'll do routine labs.
      Patient: Sure, that sounds good.
      Doctor: Your temperature is 98.4 Fahrenheit—normal. Blood pressure 118 over 76, also good.
      Patient: Good to hear.
      Doctor: Your heart sounds regular, no murmurs. Lungs are clear bilaterally. Belly is soft, no tenderness. Skin looks good—any new moles or changes?
      Patient: No, I haven't noticed anything new.
      Doctor: I'll order a CBC, metabolic panel, lipid panel, and TSH for your age. We'll call you if anything's off. Otherwise consider this a clean bill of health.
      Patient: Thank you, Doctor. When should I come back?
      Doctor: Next year for your annual, or sooner if anything changes. Stay active, eat well, and keep that stress in check.
      Patient: I will. Thanks again.
      Doctor: One more thing—are you up to date on vaccines? Flu, COVID booster, tetanus?
      Patient: I got the flu shot in October. COVID booster was last fall. Tetanus I'm not sure.
      Doctor: We can check your record. If it's been more than ten years we'll offer a Tdap. Otherwise you're all set. Take care, Ms. Chen.
      Patient: You too. Bye.
"""


if __name__ == "__main__":
    main()
