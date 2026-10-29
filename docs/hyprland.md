# Hyprland 0.55 configuration migration

The image shipped an older configuration. On the tested 0.55.2 desktop:

* Replace the obsolete workspace-swipe options with top-level `gesture = 3, horizontal, workspace`.
* Remove the obsolete `dwindle` option `pseudotile = true`.
* Use `windowrule = match:class .*, opacity 0.97 0.9` for the previous global opacity rule.
* Replace dispatcher `togglesplit` with `layoutmsg, togglesplit`, keeping the desired key binding.

Back up the existing file before editing. Reload with `hyprctl reload`, then check `hyprctl configerrors`. These edits were applied and the reported errors cleared on the test device. They are version-specific configuration edits, not a kernel display fix.
