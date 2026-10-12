import { CalculateMetadataFunction, Composition } from "remotion";
import { ReelEdit } from "./ReelEdit";
import { Edit, editDuration } from "./lib/edit";
import { frame } from "./lib/theme";

type Props = { edit: Edit };

const empty: Edit = { title: "empty", fps: frame.fps, width: frame.width, height: frame.height, clips: [], overlays: [{ type: "endCard", at: 0, dur: 3, cta: "Start with OSM" }] };

const calculateMetadata: CalculateMetadataFunction<Props> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.round(editDuration(props.edit) * props.edit.fps)),
  fps: props.edit.fps,
  width: props.edit.width,
  height: props.edit.height,
});

export const RemotionRoot: React.FC = () => (
  <Composition id="ReelEdit" component={ReelEdit} defaultProps={{ edit: empty }} calculateMetadata={calculateMetadata} width={frame.width} height={frame.height} fps={frame.fps} durationInFrames={90} />
);
