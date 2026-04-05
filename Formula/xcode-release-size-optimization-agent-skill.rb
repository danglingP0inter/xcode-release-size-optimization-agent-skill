class XcodeReleaseSizeOptimizationAgentSkill < Formula
  desc "CLI and agent skill suite for analyzing Xcode release build size"
  homepage "https://github.com/danglingP0inter/xcode-release-size-optimization-agent-skill"
  head "https://github.com/danglingP0inter/xcode-release-size-optimization-agent-skill.git", branch: "main"

  depends_on "node"
  depends_on "python@3.14"

  def install
    libexec.install "AGENTS.md", "CLAUDE.md", "README.md", "agents", "bin", "package.json", "references", "scripts", "skills"

    (bin/"xcode-release-size-skill").write <<~SH
      #!/bin/bash
      export PYTHON="#{Formula["python@3.14"].opt_bin}/python3"
      exec "#{Formula["node"].opt_bin}/node" "#{libexec}/bin/xcode-release-size-skill.js" "$@"
    SH
    chmod 0755, bin/"xcode-release-size-skill"
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/xcode-release-size-skill --help")
  end
end
