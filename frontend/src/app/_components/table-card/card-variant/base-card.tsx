import React from 'react';
import { IconDotsVertical } from '@tabler/icons-react';
import cslx from 'clsx';
import {
  ActionIcon,
  Card,
  Checkbox,
  Divider,
  Group,
  Menu,
  Radio,
  rem,
} from '@mantine/core';
import {
  DefaultCardBody,
  DefaultCardBottomActionButton,
  DefaultCardBottomRightActionButton,
  DefaultCardExtraButton,
  DefaultCardExtraStatus,
  DefaultCardImage,
  DefaultCardInformationText,
  DefaultCardInputField,
  DefaultCardLabel,
  DefaultCardLowerBody,
  DefaultCardPriceTag,
  DefaultCardProgressBar,
  DefaultCardRating,
  DefaultCardStatus,
  DefaultCardSubtitle,
  DefaultCardSubtitleRightButton,
  DefaultCardTag,
  DefaultCardTagWrapper,
  DefaultCardTitle,
  DefaultCardTitleRightButton,
} from './card-fields';
import { getAlignmentStyle } from './utils';

type TCardLayout = 'horizontal' | 'vertical';
export type TRowAlignment = 'left' | 'right' | 'center';

type TFlexibleContent =
  | React.ReactNode
  | React.ReactNode[]
  | React.ReactNode[][];

export interface IBaseCardProps {
  layout?: TCardLayout;

  // Leading
  image?: TFlexibleContent;
  leading?: React.ReactNode;
  withCheckbox?: boolean;
  checked?: boolean;
  onCheckChange?: (checked: boolean) => void;
  withRadio?: boolean;
  radioValue?: string;
  radioSelected?: boolean;
  onRadioChange?: (value: string) => void;

  // Header
  label?: TFlexibleContent;
  status?: TFlexibleContent;

  // Title Section
  title?: TFlexibleContent;
  subtitle?: TFlexibleContent;

  // Body
  body?: TFlexibleContent;
  lowerBody?: TFlexibleContent;
  autoField?: TFlexibleContent;

  // Meta
  rating?: TFlexibleContent; // Can be number or ReactNode
  tags?: TFlexibleContent;
  progressBar?: TFlexibleContent; // Can be number (0-100) or ReactNode
  informationText?: TFlexibleContent;
  priceTag?: TFlexibleContent;
  extraStatus?: TFlexibleContent;

  // Inputs
  inputField?: TFlexibleContent; // Placeholder string or ReactNode

  // Actions
  titleRightButton?: TFlexibleContent;
  subtitleRightButton?: TFlexibleContent;

  // Button Actions - Now expecting ReactNode mostly, but keeping flexibility
  bottomActionButton?: TFlexibleContent;
  bottomLeftActionButton?: TFlexibleContent;
  bottomRightActionButton?: TFlexibleContent;

  extraButton?: TFlexibleContent;

  // Trailing
  withContextMenu?: boolean;
  contextMenu?: React.ReactNode; // Custom menu items or full menu

  // Events
  onClick?: () => void;
  className?: string;
}

interface ICardImageSectionProps {
  isHorizontalLayout: boolean;
  image: TFlexibleContent;
}

interface ICardLeadingSectionProps extends Pick<
  IBaseCardProps,
  | 'leading'
  | 'withCheckbox'
  | 'checked'
  | 'onCheckChange'
  | 'withRadio'
  | 'radioValue'
  | 'radioSelected'
  | 'onRadioChange'
> {}

interface ICardMainContentSectionProps extends Pick<
  IBaseCardProps,
  | 'label'
  | 'status'
  | 'title'
  | 'subtitle'
  | 'titleRightButton'
  | 'subtitleRightButton'
  | 'tags'
  | 'rating'
  | 'lowerBody'
  | 'body'
  | 'progressBar'
  | 'informationText'
  | 'priceTag'
  | 'extraStatus'
  | 'inputField'
  | 'bottomActionButton'
  | 'bottomLeftActionButton'
  | 'bottomRightActionButton'
> {}

interface ICardContextMenuSectionProps extends Pick<
  IBaseCardProps,
  'withContextMenu' | 'contextMenu'
> {}

interface ICardLeadingSectionWrapper {
  children: React.ReactNode;
}

// Helper to render content flexibly
function renderField(
  defaultRender: (item: any, index?: number) => React.ReactNode,
  content?: TFlexibleContent,
  wrapperComponent?: (children: React.ReactNode) => React.ReactNode,
  rowAlignment?: TRowAlignment
) {
  if (content === undefined || content === null) {
    return null;
  }

  // Helper to render a single item or 1D array of items
  const renderRowItems = (rowContent: any) => {
    if (Array.isArray(rowContent)) {
      return rowContent.map((item, index) => (
        <React.Fragment key={index}>
          {React.isValidElement(item) ? item : defaultRender(item, index)}
        </React.Fragment>
      ));
    }

    return React.isValidElement(rowContent)
      ? rowContent
      : defaultRender(rowContent);
  };

  // Check for 2D array: Array of Arrays (First item is array)
  if (
    Array.isArray(content) &&
    content.length > 0 &&
    Array.isArray(content[0])
  ) {
    const alignmentStyle = getAlignmentStyle(rowAlignment);

    return (
      <div className="flex w-full flex-col gap-1">
        {content.map((row: any, rowIndex: number) => (
          <React.Fragment key={rowIndex}>
            {wrapperComponent ? (
              wrapperComponent(renderRowItems(row))
            ) : (
              <div
                className={cslx(
                  'flex flex-wrap items-center gap-2',
                  alignmentStyle
                )}
              >
                {renderRowItems(row)}
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  const renderedContent = renderRowItems(content);
  return wrapperComponent ? wrapperComponent(renderedContent) : renderedContent;
}

export default function BaseCard({
  layout = 'horizontal',
  ...props
}: IBaseCardProps) {
  const isClickable = Boolean(props.onClick);
  const isHorizontalLayout = layout === 'horizontal';
  const showContextMenu = props.contextMenu || props.withContextMenu;
  const showExtraButton = props.extraButton && isHorizontalLayout;

  return (
    <Card
      shadow="sm"
      padding="xs"
      radius="md"
      withBorder
      className={cslx(
        'flex h-full w-full flex-col transition-shadow duration-200 hover:shadow-md',
        props.className,
        isClickable ? 'cursor-pointer' : ''
      )}
      onClick={props.onClick}
    >
      {/* Vertical Layout: Image on Top (Card.Section) */}
      {!isHorizontalLayout && props.image && (
        <Card.Section>
          <CardImageSection
            isHorizontalLayout={isHorizontalLayout}
            image={props.image}
          />
        </Card.Section>
      )}

      <div
        className={cslx(
          'flex flex-1 gap-2.5',
          !isHorizontalLayout ? 'mt-2' : null
        )}
      >
        {/* Leading */}
        <CardLeadingSection {...props} />

        {/* Content Layout */}
        <div
          className={cslx(
            'flex flex-1 flex-col gap-2',
            isHorizontalLayout ? 'sm:flex-row' : null
          )}
        >
          {/* Horizontal Layout: Image Inline */}
          {isHorizontalLayout && (
            <CardImageSection isHorizontalLayout image={props.image} />
          )}

          <CardMainContentSection {...props} />

          {/* Extra Button (Right Side - Desktop - usually only horizontal) */}
          {showExtraButton && (
            <div className="hidden flex-col justify-center border-l border-gray-100 pl-2 sm:flex">
              {renderField(
                (text) => (
                  <DefaultCardExtraButton text={text} />
                ),
                props.extraButton
              )}
            </div>
          )}
        </div>

        {/* Trailing Context Menu */}
        {showContextMenu && (
          <CardContextMenuSection contextMenu={props.contextMenu} />
        )}
      </div>
    </Card>
  );
}

function CardImageSection({
  isHorizontalLayout,
  image,
}: ICardImageSectionProps) {
  if (!image) {
    return null;
  }

  const fallbackImageDimension = {
    height: isHorizontalLayout ? 80 : 400,
    width: isHorizontalLayout ? 80 : 300,
  };

  return (
    <div
      className={cslx(
        'shrink-0',
        isHorizontalLayout ? 'mx-auto h-20 w-20 sm:mx-0' : 'h-48 w-full'
      )}
    >
      {renderField(
        (src) => (
          <DefaultCardImage
            src={src}
            fallbackImageDimensions={fallbackImageDimension}
          />
        ),
        image
      )}
    </div>
  );
}

function CardMainContentSection({
  label,
  status,
  title,
  subtitle,
  titleRightButton,
  subtitleRightButton,
  tags,
  rating,
  lowerBody,
  body,
  progressBar,
  informationText,
  priceTag,
  extraStatus,
  inputField,
  bottomActionButton,
  bottomLeftActionButton,
  bottomRightActionButton,
}: ICardMainContentSectionProps) {
  const showBottomActionButton =
    bottomActionButton || bottomLeftActionButton || bottomRightActionButton;
  const showLabelOrStatus = label || status;
  const showRatingOrLowerBody = rating || lowerBody;

  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1">
      {/* Header Row: Label & Status */}
      {showLabelOrStatus && (
        <Group gap={4}>
          {label &&
            renderField((text) => <DefaultCardLabel text={text} />, label)}
          {renderField(
            (text) => (
              <DefaultCardStatus text={text} />
            ),
            status
          )}
        </Group>
      )}

      {/* Title & Subtitle Row */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          {renderField(
            (text) => (
              <DefaultCardTitle text={text} />
            ),
            title
          )}
          {renderField(
            (text) => (
              <DefaultCardSubtitle text={text} />
            ),
            subtitle
          )}
        </div>

        {/* Right Title Actions */}
        <div className="flex shrink-0 flex-col items-end gap-0.5">
          {renderField(
            (text) => (
              <DefaultCardTitleRightButton text={text} />
            ),
            titleRightButton
          )}
          {renderField(
            (text) => (
              <DefaultCardSubtitleRightButton text={text} />
            ),
            subtitleRightButton
          )}
        </div>
      </div>

      {/* Service Tags */}
      {renderField(
        (text) => (
          <DefaultCardTag text={text} />
        ),
        tags,
        (children) => (
          <DefaultCardTagWrapper>{children}</DefaultCardTagWrapper>
        )
      )}

      {/* Rating & Lower Body */}
      <Group gap="xs" align="center" className="flex-wrap">
        {renderField(
          (text) => (
            <DefaultCardRating text={text} />
          ),
          rating
        )}

        {showRatingOrLowerBody && (
          <Divider orientation="vertical" className="hidden sm:block" />
        )}

        {renderField(
          (text) => (
            <DefaultCardLowerBody text={text} />
          ),
          lowerBody
        )}
      </Group>

      {/* Body Text */}
      {renderField(
        (text) => (
          <DefaultCardBody text={text} />
        ),
        body
      )}

      {/* Progress Bar */}
      {renderField(
        (value) => (
          <DefaultCardProgressBar text={value} />
        ),
        progressBar
      )}

      {/* Text Icon & Price */}
      <Group justify="space-between" align="center" className="mt-1">
        {renderField(
          (text) => (
            <DefaultCardInformationText text={text} />
          ),
          informationText
        )}
        {renderField(
          (text) => (
            <DefaultCardPriceTag text={text} />
          ),
          priceTag
        )}
      </Group>

      {/* Extra Status */}
      {renderField(
        (text) => (
          <DefaultCardExtraStatus text={text} />
        ),
        extraStatus
      )}

      {/* Input Field */}
      {renderField(
        (placeholder) => (
          <DefaultCardInputField text={placeholder} />
        ),
        inputField
      )}

      {/* Bottom Actions */}
      {showBottomActionButton && (
        <div className="mt-auto flex flex-wrap gap-2 border-t border-gray-100 pt-2">
          {renderField(
            (content) => (
              <DefaultCardBottomActionButton content={content} />
            ),
            bottomActionButton
          )}
          <div className="ml-auto flex w-full gap-2 sm:w-auto">
            {renderField(
              (content) => (
                <DefaultCardBottomActionButton content={content} />
              ),
              bottomLeftActionButton,
              undefined,
              'left'
            )}
            {renderField(
              (content) => (
                <DefaultCardBottomRightActionButton content={content} />
              ),
              bottomRightActionButton,
              undefined,
              'right'
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function CardLeadingSectionWrapper({ children }: ICardLeadingSectionWrapper) {
  return <div className="flex items-center pt-0.5">{children}</div>;
}

function CardLeadingSection({
  leading,
  withCheckbox,
  checked,
  onCheckChange,
  withRadio,
  radioValue,
  radioSelected,
  onRadioChange,
}: ICardLeadingSectionProps) {
  let content: React.ReactNode = null;

  if (leading) {
    content = leading;
  } else if (withCheckbox) {
    content = (
      <Checkbox
        radius="sm"
        checked={checked}
        onChange={(event) => onCheckChange?.(event.currentTarget.checked)}
      />
    );
  } else if (withRadio) {
    content = (
      <Radio
        value={radioValue}
        checked={radioSelected}
        onChange={(event) => onRadioChange?.(event.currentTarget.value)}
      />
    );
  }

  if (!content) {
    return null;
  }

  return <CardLeadingSectionWrapper>{content}</CardLeadingSectionWrapper>;
}

function CardContextMenuSection({
  contextMenu,
  withContextMenu,
}: ICardContextMenuSectionProps) {
  const shouldRenderMenu = contextMenu || withContextMenu;

  return (
    <div className="flex items-start">
      <Menu shadow="md" width={150} position="bottom-end">
        <Menu.Target>
          <ActionIcon variant="subtle" color="gray" size="sm">
            <IconDotsVertical style={{ width: rem(14), height: rem(14) }} />
          </ActionIcon>
        </Menu.Target>
        <Menu.Dropdown>
          {shouldRenderMenu || <Menu.Item>Tidak ada action</Menu.Item>}
        </Menu.Dropdown>
      </Menu>
    </div>
  );
}
