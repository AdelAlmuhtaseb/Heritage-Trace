import { type ParamListBase, type TabNavigationState } from '@react-navigation/native';
import type { BottomTabDescriptorMap, BottomTabNavigationConfig, BottomTabNavigationHelpers } from '../types.js';
type Props = BottomTabNavigationConfig & {
    state: TabNavigationState<ParamListBase>;
    navigation: BottomTabNavigationHelpers;
    descriptors: BottomTabDescriptorMap;
};
export declare function BottomTabView(props: Props): import("react/jsx-runtime").JSX.Element;
export {};
//# sourceMappingURL=BottomTabView.d.ts.map