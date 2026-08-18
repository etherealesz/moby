import BaseCard, { IBaseCardProps } from './base-card';

export interface ICardHorizontalProps extends IBaseCardProps {
  data?: IBaseCardProps | any;
  onClick?: () => void;
}

export default function CardHorizontal(props: ICardHorizontalProps) {
  // Merge data object with direct props. Direct props take precedence.
  const { data, ...directProps } = props;
  const combinedData: IBaseCardProps = { ...data, ...directProps };

  // Final props to be passed to BaseCard
  const mappedProps: IBaseCardProps = {
    ...combinedData,
    lowerBody: combinedData.lowerBody || combinedData.lowerBody,
    tags: combinedData.tags || combinedData.tags,
    autoField: combinedData.autoField || combinedData.autoField,
    informationText:
      combinedData.informationText || combinedData.informationText,
    priceTag: combinedData.priceTag || combinedData.priceTag,
    extraStatus: combinedData.extraStatus || combinedData.extraStatus,
    inputField: combinedData.inputField || combinedData.inputField,
    titleRightButton:
      combinedData.titleRightButton || combinedData.titleRightButton,
    subtitleRightButton:
      combinedData.subtitleRightButton || combinedData.subtitleRightButton,
    bottomActionButton:
      combinedData.bottomActionButton || combinedData.bottomActionButton,
    bottomLeftActionButton:
      combinedData.bottomLeftActionButton ||
      combinedData.bottomLeftActionButton,
    bottomRightActionButton:
      combinedData.bottomRightActionButton ||
      combinedData.bottomRightActionButton,
    extraButton: combinedData.extraButton || combinedData.extraButton,
    progressBar: combinedData.progressBar || combinedData.progressBar,
    layout: 'horizontal', // Force horizontal layout
  };

  return <BaseCard {...mappedProps} />;
}
