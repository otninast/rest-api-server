BUILD_DIR="."
REGION="ap-northeast-1"
APP_NAME="rest-api-server"
DEPLOYMENT_GROUP="rest-api-server-group"
DEPLOYMENT_CONFIG="CodeDeployDefault.AllAtOnce"
S3_BUCKET="rest-api-server"
TAG=`date '+%Y%m%d%H%M'`
S3_KEY=dev/${APP_NAME}_$TAG.zip


echo "#### create CodeDeploy revision: ${S3_KEY}"

aws deploy push \
        --region ${REGION} \
        --application-name ${APP_NAME} \
        --s3-location s3://${S3_BUCKET}/${S3_KEY} \
        --source ${BUILD_DIR} \
        --debug



echo "#### deployment revision: ${S3_KEY}"

ETAG=`aws deploy list-application-revisions \
        --region ${REGION} \
        --application-name ${APP_NAME} \
        --s-3-bucket ${S3_BUCKET} \
        --s-3-key-prefix ${S3_KEY} \
        --query 'revisions[0].s3Location.eTag' \
        --output text` \
        --debug



aws deploy create-deployment \
        --region ${REGION} \
        --application-name ${APP_NAME} \
        --s3-location bucket=${S3_BUCKET},key=${S3_KEY},bundleType=zip,eTag=${ETAG} \
        --deployment-group-name ${DEPLOYMENT_GROUP} \
        --deployment-config-name ${DEPLOYMENT_CONFIG} \
        --debug

# echo ""

echo ${ETAG}
