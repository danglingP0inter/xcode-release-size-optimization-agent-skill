import SwiftUI

struct ContentView: View {
    private let highlights = [
        "Release-size baseline",
        "Binary attribution",
        "Resource categorization",
        "Approval-gated fixes"
    ]

    var body: some View {
        NavigationStack {
            List {
                Section("Skill Suite Validation") {
                    ForEach(highlights, id: \.self) { item in
                        Label(item, systemImage: "shippingbox")
                    }
                }

                Section("Bundled Payload") {
                    Text("This sample app exists so the skill suite can validate a real archive, bundle, and IPA workflow.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Size Validation")
        }
    }
}
