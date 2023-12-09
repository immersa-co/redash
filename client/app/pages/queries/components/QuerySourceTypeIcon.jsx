import PropTypes from "prop-types";
import React from "react";

export function QuerySourceTypeIcon(props) {
  const ds_image_name = (props.type && props.type.includes('lo_')) ? 'lo_icon' : props.type
  return <img src={`/static/images/db-logos/${ds_image_name}.png`} width="20" alt={props.alt} />;
}

QuerySourceTypeIcon.propTypes = {
  type: PropTypes.string,
  alt: PropTypes.string,
};
